import shutil
import tempfile
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings

from catalog.models import Category, Item, ItemImage, ItemInt, Tag

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

# Минимальная валидная картинка 1x1 (GIF)
GIF_BYTES = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01"
    b"\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


def make_image(name="test.gif"):
    return SimpleUploadedFile(name, GIF_BYTES, content_type="image/gif")


class NamedSlugModelTestsMixin:
    """Общие тесты для Category и Tag: у них одинаковые поля name и slug."""

    model = None
    verbose_name = None
    verbose_name_plural = None

    def test_slug_generated_from_name(self):
        """Если слаг не задан, он автоматически создаётся из названия."""
        obj = self.model.objects.create(name="Hello World")
        self.assertEqual(obj.slug, "hello-world")

    def test_custom_slug_is_not_overwritten(self):
        """Слаг, заданный вручную, не перезаписывается при сохранении."""
        obj = self.model.objects.create(name="Hello World", slug="custom")
        self.assertEqual(obj.slug, "custom")

    def test_slug_not_changed_on_rename(self):
        """При переименовании объекта его слаг остаётся прежним."""
        obj = self.model.objects.create(name="First name")
        obj.name = "Second name"
        obj.save()
        obj.refresh_from_db()
        self.assertEqual(obj.slug, "first-name")

    def test_name_is_unique(self):
        """Нельзя создать два объекта с одинаковым названием."""
        self.model.objects.create(name="Same")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.model.objects.create(name="Same", slug="other")

    def test_slug_is_unique(self):
        """Нельзя создать два объекта с одинаковым слагом."""
        self.model.objects.create(name="One", slug="same-slug")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.model.objects.create(name="Two", slug="same-slug")

    def test_name_max_length(self):
        """Название длиннее 150 символов не проходит валидацию."""
        obj = self.model(name="x" * 151)
        with self.assertRaises(ValidationError) as ctx:
            obj.full_clean()
        self.assertIn("name", ctx.exception.message_dict)

    def test_verbose_names(self):
        """У модели заданы правильные русские названия в админке."""
        self.assertEqual(self.model._meta.verbose_name, self.verbose_name)
        self.assertEqual(self.model._meta.verbose_name_plural, self.verbose_name_plural)

    def test_cyrillic_name_gets_non_empty_slug(self):
        """Русские названия получают непустые и разные слаги."""
        a = self.model.objects.create(name="Книги")
        b = self.model.objects.create(name="Одежда")
        self.assertNotEqual(a.slug, "")
        self.assertNotEqual(a.slug, b.slug)


class CategoryModelTests(NamedSlugModelTestsMixin, TestCase):
    model = Category
    verbose_name = "Категория"
    verbose_name_plural = "Категории"


class TagModelTests(NamedSlugModelTestsMixin, TestCase):
    model = Tag
    verbose_name = "Тег"
    verbose_name_plural = "Теги"


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ItemModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Electronics")
        cls.tag1 = Tag.objects.create(name="new")
        cls.tag2 = Tag.objects.create(name="sale")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def make_item(self, **kwargs):
        data = {"name": "Phone", "category": self.category}
        data.update(kwargs)
        return Item.objects.create(**data)

    def test_slug_generated_from_name(self):
        """Слаг товара автоматически создаётся из его названия."""
        item = self.make_item(name="Big Phone")
        self.assertEqual(item.slug, "big-phone")

    def test_custom_slug_is_not_overwritten(self):
        """Слаг товара, заданный вручную, не перезаписывается."""
        item = self.make_item(slug="my-slug")
        self.assertEqual(item.slug, "my-slug")

    def test_name_is_unique(self):
        """Нельзя создать два товара с одинаковым названием."""
        self.make_item(name="Dup")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_item(name="Dup", slug="other")

    def test_str_returns_first_15_characters(self):
        """Строковое представление длинного названия обрезается до 15 символов."""
        item = self.make_item(name="A" * 40)
        self.assertEqual(str(item), "A" * 15)

    def test_str_short_name_is_unchanged(self):
        """Короткое название в строковом представлении не меняется."""
        item = self.make_item(name="Short")
        self.assertEqual(str(item), "Short")

    def test_defaults(self):
        """Текст, описание и главное фото по умолчанию пустые."""
        item = self.make_item()
        self.assertEqual(item.text, "")
        self.assertEqual(item.description, "")
        self.assertFalse(item.main_image)

    def test_created_and_updated_at_are_set(self):
        """При создании товара автоматически заполняются даты создания и изменения."""
        item = self.make_item()
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)

    def test_updated_at_changes_on_save_but_created_at_does_not(self):
        """При сохранении обновляется только дата изменения, а дата создания нет."""
        item = self.make_item()
        created = item.created_at
        old = created - timedelta(days=1)
        Item.objects.filter(pk=item.pk).update(updated_at=old)

        item.refresh_from_db()
        item.description = "changed"
        item.save()
        item.refresh_from_db()

        self.assertEqual(item.created_at, created)
        self.assertGreater(item.updated_at, old)

    def test_text_longer_than_150_is_invalid(self):
        """Текст длиннее 150 символов не проходит валидацию."""
        item = Item(name="Long", category=self.category, text="x" * 151)
        with self.assertRaises(ValidationError) as ctx:
            item.full_clean()
        self.assertIn("text", ctx.exception.message_dict)

    def test_category_is_required(self):
        """Нельзя создать товар без категории."""
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Item.objects.create(name="No category")

    def test_related_name_items_on_category(self):
        """Товары категории доступны через category.items."""
        item = self.make_item()
        self.assertIn(item, self.category.items.all())

    def test_tags_many_to_many(self):
        """К товару можно привязать несколько тегов, и связь работает в обе стороны."""
        item = self.make_item()
        item.tags.add(self.tag1, self.tag2)
        self.assertEqual(item.tags.count(), 2)
        self.assertIn(item, self.tag1.item_set.all())

    def test_deleting_category_deletes_items(self):
        """При удалении категории удаляются все её товары."""
        self.make_item()
        self.category.delete()
        self.assertEqual(Item.objects.count(), 0)

    def test_deleting_tag_keeps_item(self):
        """При удалении тега товар остаётся, пропадает только связь с тегом."""
        item = self.make_item()
        item.tags.add(self.tag1)
        self.tag1.delete()
        self.assertTrue(Item.objects.filter(pk=item.pk).exists())
        self.assertEqual(item.tags.count(), 0)

    def test_main_image_can_be_saved(self):
        """Главное фото сохраняется в папку items/main."""
        item = self.make_item(main_image=make_image())
        self.assertTrue(item.main_image.name.startswith("items/main/"))

    def test_verbose_names(self):
        """У модели Item заданы правильные русские названия в админке."""
        self.assertEqual(Item._meta.verbose_name, "Товар")
        self.assertEqual(Item._meta.verbose_name_plural, "Товары")


class ItemIntModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Cat")
        cls.item = Item.objects.create(name="Thing", category=category)

    def test_default_stock_is_zero(self):
        """Количество товара по умолчанию равно нулю."""
        self.assertEqual(ItemInt.objects.create(item=self.item).stock, 0)

    def test_str(self):
        """Строковое представление показывает название товара и его количество."""
        obj = ItemInt.objects.create(item=self.item, stock=5)
        self.assertEqual(str(obj), "Количество Thing равно: 5")

    def test_negative_stock_is_invalid(self):
        """Отрицательное количество не проходит валидацию."""
        obj = ItemInt(item=self.item, stock=-1)
        with self.assertRaises(ValidationError) as ctx:
            obj.full_clean()
        self.assertIn("stock", ctx.exception.message_dict)

    def test_related_name(self):
        """Записи о количестве доступны через related_name Количество_товаров."""
        obj = ItemInt.objects.create(item=self.item, stock=3)
        self.assertIn(obj, getattr(self.item, "Количество_товаров").all())

    def test_deleting_item_deletes_stock(self):
        """При удалении товара удаляются и записи о его количестве."""
        ItemInt.objects.create(item=self.item, stock=3)
        self.item.delete()
        self.assertEqual(ItemInt.objects.count(), 0)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ItemImageModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Cat")
        cls.item = Item.objects.create(name="Thing", category=category)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_image_is_saved_to_extra_folder(self):
        """Дополнительное фото сохраняется в папку items/extra."""
        obj = ItemImage.objects.create(item=self.item, image=make_image())
        self.assertTrue(obj.image.name.startswith("items/extra/"))

    def test_related_name(self):
        """Фото товара доступны через related_name фото."""
        obj = ItemImage.objects.create(item=self.item, image=make_image())
        self.assertIn(obj, getattr(self.item, "фото").all())

    def test_image_is_required(self):
        """Запись без файла картинки не проходит валидацию."""
        obj = ItemImage(item=self.item)
        with self.assertRaises(ValidationError) as ctx:
            obj.full_clean()
        self.assertIn("image", ctx.exception.message_dict)

    def test_deleting_item_deletes_images(self):
        """При удалении товара удаляются и все его дополнительные фото."""
        ItemImage.objects.create(item=self.item, image=make_image())
        self.item.delete()
        self.assertEqual(ItemImage.objects.count(), 0)
