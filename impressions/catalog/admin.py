from django.contrib import admin

import catalog.models


@admin.register(catalog.models.Item)
class ItemAdmin(admin.ModelAdmin):
    # Все что мы отображаем
    list_display = [
        "name",
        "is_published",
    ]

    # Все что мы можем сразу редактировать
    list_editable = ("is_published",)

    # Элименты отображающиеся как ссылки
    list_display_links = ("name",)


@admin.register(catalog.models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]


@admin.register(catalog.models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
