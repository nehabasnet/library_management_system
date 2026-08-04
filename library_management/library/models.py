from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Categories'

class Book(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True, blank=True, default='')
    description = models.TextField(blank=True, default='')
    quantity = models.IntegerField(default=1)
    available = models.BooleanField(default=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)  # ← file upload
    cover_url   = models.URLField(blank=True, default='')
    book_file   = models.FileField(upload_to='book_files/', blank=True, null=True)
    read_url    = models.URLField(blank=True, default='')
 

    def __str__(self):
        return self.title
    
    def get_cover(self):
        """Returns whichever cover is available — uploaded file takes priority."""
        if self.cover_image:
            return self.cover_image.url
        if self.cover_url:
            return self.cover_url
        return None
class ContactInfo(models.Model):
    library_name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    opening_hours = models.CharField(max_length=255)

    def __str__(self):
        return self.library_name
    

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

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} — {self.name}"

    class Meta:
        ordering = ['-created_at']