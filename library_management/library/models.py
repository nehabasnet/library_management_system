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