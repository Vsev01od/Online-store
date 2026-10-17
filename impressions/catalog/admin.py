from django.contrib import admin
from .models import Category, Item, ItemImage, Tag

class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1
class ItemAdmin(admin.ModelAdmin):
    #видим заходя на каталог наших продуктов
    list_display = ["name", "category", "price"]

    #по каким полям фильтрация
    list_filter = ["category"]

    #по каким полям поиск
    search_fields = ["name", "description"]

    #позволяет заполнять параметры из тех параметров которые у нас уже есть
    prepopulated_fields = {"slug":("name",)}


    inlines = [ItemImageInline]


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug":("name",)}


class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug":("name",)}


admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Item, ItemAdmin)