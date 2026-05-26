from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    category    = models.ForeignKey(Category, on_delete=models.CASCADE)
    title       = models.CharField(max_length=200)
    author      = models.CharField(max_length=200)
    isbn        = models.CharField(max_length=13, unique=True)
    description = models.TextField(blank=True, default='')
    quantity    = models.IntegerField(default=1)

    def available(self):
        issued = IssueBook.objects.filter(book=self, return_date__isnull=True).count()
        return self.quantity - issued

    def __str__(self):
        return f"{self.title} by {self.author}"


class Student(models.Model):
    full_name  = models.CharField(max_length=200)
    student_id = models.CharField(max_length=50, unique=True)
    email      = models.EmailField()
    phone      = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.full_name} ({self.student_id})"


class IssueBook(models.Model):
    student     = models.ForeignKey(Student, on_delete=models.CASCADE)
    book        = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date  = models.DateField(auto_now_add=True)
    due_date    = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine        = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.student} → {self.book}"