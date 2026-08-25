from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator

from catalog.validators import validators_item
from base_model.models import BaseModelIsPublished


class Category(BaseModelIsPublished):
    name = models.CharField("Название", unique=True)

    slug = models.CharField(
        "Слаг",
        validators=[
            MaxLengthValidator(150),
        ],
        default="",
        blank=True,
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Tag(BaseModelIsPublished):
    name = models.CharField(
        "Имя",
        validators=[
            MinLengthValidator(2),
        ],
        help_text="Имя должнобыть больше, чем из 2х букв",
        # Уникальность
        unique=True,
    )

    slug = models.CharField(
        "Слаг",
        validators=[
            MaxLengthValidator(150),
        ],
        default="",
        blank=True,
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Item(BaseModelIsPublished):
    name = models.CharField(
        "Имя",
        validators=[
            MinLengthValidator(2),
        ],
        help_text="Имя должнобыть больше, чем из 2х букв",
    )

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

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        # Показывает только 15 первых символов
        return self.name[:15]
