from django.shortcuts import render
import django.http


def index(request):
    return django.http.HttpResponse("<body>Hello, word</body>")
