from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.text import slugify

from catalog.validators import validators_item
from base_model.models import BaseModelIsPublished

from django.utils import timezone


class Category(BaseModelIsPublished):
    name = models.CharField("Название", max_length=150, unique=True)
    slug = models.SlugField("Слаг", max_length=150, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Tag(BaseModelIsPublished):
    name = models.CharField("Название", max_length=150, unique=True)
    slug = models.SlugField("Слаг", max_length=150, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class ItemInt(models.Model):
    item = models.ForeignKey(
        "Item", on_delete=models.CASCADE, related_name="Количество_товаров"
    )
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Количество {self.item.name} равно: {self.stock}"


class Item(BaseModelIsPublished):
    name = models.CharField("Название", max_length=150, unique=True)
    slug = models.SlugField("Слаг", max_length=150, blank=True, unique=True)
    text = models.TextField(
        "Описание",
        validators=[
            MaxLengthValidator(150),
            validators_item,
        ],
        help_text="Описание должно быть не больше чем 150 букв",
        default="",
        blank=True,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="items",
    )

    tags = models.ManyToManyField(Tag)
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to="items/main", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        # Показывает только 15 первых символов
        return self.name[:15]


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="фото")
    image = models.ImageField(upload_to="items/extra")
