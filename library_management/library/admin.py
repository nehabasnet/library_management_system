from django.contrib import admin
from .models import Book, Category
from .models import ContactInfo, Reservation

admin.site.register(Book)
admin.site.register(Category)
admin.site.register(ContactInfo)
admin.site.register(Reservation)
