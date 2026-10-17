from django.shortcuts import render
import django.http


def index(request):
    template = "home/home.html"
    context = {}
    return render(request, template, context)
