from django.contrib import admin
from django.urls import path
import home.views

urlpatterns = [
    path("", home.views.index),
    path("admin/", admin.site.urls),
]
