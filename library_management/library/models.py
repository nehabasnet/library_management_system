from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=200)

    author = models.CharField(max_length=200)

    description = models.TextField(blank=True, default='')

    quantity = models.IntegerField(default=1)

    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title
class ContactInfo(models.Model):
    library_name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    opening_hours = models.CharField(max_length=255)

    def __str__(self):
        return self.library_name