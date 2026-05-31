from django.contrib import admin
from .models import Book, Category
from .models import ContactInfo

admin.site.register(Book)
admin.site.register(Category)
admin.site.register(ContactInfo)
# Register your models here.
