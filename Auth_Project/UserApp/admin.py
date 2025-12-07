from django.contrib import admin
from .models import Category, File, FileCategoryMapping

admin.site.register(Category)
admin.site.register(File)
admin.site.register(FileCategoryMapping)
