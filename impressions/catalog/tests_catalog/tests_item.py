from django.test import TestCase
from catalog.models import Item, Tag, Category
from django.core import validators


class TestItem(TestCase):
    fixtures = ["catalog.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tag = Tag.objects.create(name="тег")
        cls.category = Category.objects.create(name="категория")

        return cls

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.tag.delete()
        cls.category.delete()

        return cls

    def test_item_create(self):
        item_count = Item.objects.count()

        item = Item.objects.create(name="товар", category=self.category)
        item.tags.set([self.tag])

        self.assertEqual(Item.objects.count(), item_count + 1)

    def test_item_create_error(self):
        item_count = Item.objects.count()
        item = Item(name="т", category=self.category)
        with self.assertRaises(validators.ValidationError):
            item.full_clean()
        self.assertEqual(Item.objects.count(), item_count)
