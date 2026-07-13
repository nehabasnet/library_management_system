from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Book, Category, ContactInfo, Student, IssueBook

def home(request):
    return render(request, 'library/index.html')

# User Authentication Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

        else:
            return render(request, 'library/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'library/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# Book Views
def books(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    books = Book.objects.all().order_by('category__name')
    categories = Category.objects.all()

    if category_id:
        books = books.filter(category_id=category_id)

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(category__name__icontains=query)
        )

    return render(request, 'library/books.html', {
        'books': books,
        'categories': categories,
        'selected_category': category_id,
    })
def contact(request):
    contact = ContactInfo.objects.first()

    return render(request, 'library/contact.html', {
        'contact': contact
    })
def about(request):
    return render(request, 'library/about.html')
# admin dashboard
@login_required
def dashboard(request):
    return render(request, 'library/dashboard.html')

@login_required
def book_management(request):
    query      = request.GET.get('q', '')
    categories = Category.objects.all()
    books      = Book.objects.select_related('category').all()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    return render(request, 'library/book_management.html', {
        'books': books, 'categories': categories, 'query': query,
    })


@login_required
def book_add(request):
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        author      = request.POST.get('author', '').strip()
        isbn        = request.POST.get('isbn', '').strip()
        quantity    = request.POST.get('quantity', 1)
        desc        = request.POST.get('description', '').strip()
        cover_url   = request.POST.get('cover_url', '').strip()
        cat_id      = request.POST.get('category')
        new_cat     = request.POST.get('new_category', '').strip()
        cover_image = request.FILES.get('cover_image')   # ← file upload

        if new_cat:
            category, _ = Category.objects.get_or_create(name=new_cat)
        elif cat_id and cat_id != 'new':
            category = get_object_or_404(Category, id=cat_id)
        else:
            messages.error(request, 'Please select or enter a category.')
            return redirect('book_management')

        if isbn and Book.objects.filter(isbn=isbn).exists():
            messages.error(request, f'A book with ISBN "{isbn}" already exists.')
            return redirect('book_management')

        Book.objects.create(
            title=title, author=author, isbn=isbn,
            quantity=quantity, description=desc,
            category=category, available=True,
            cover_image=cover_image,             # ← new
            cover_url=cover_url                  # ← new
        )
        messages.success(request, f'"{title}" added successfully!')
    return redirect('book_management')


@login_required
def book_edit(request, pk):
    book       = get_object_or_404(Book, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        book.title       = request.POST.get('title', '').strip()
        book.author      = request.POST.get('author', '').strip()
        book.isbn        = request.POST.get('isbn', '').strip()
        book.quantity    = request.POST.get('quantity', 1)
        book.description = request.POST.get('description', '').strip()
        book.cover_url   = request.POST.get('cover_url', '').strip()
        cat_id = request.POST.get('category')
        if cat_id:
            book.category = get_object_or_404(Category, id=cat_id)
        # Only update image if a new one was uploaded
        if request.FILES.get('cover_image'):
            book.cover_image = request.FILES.get('cover_image')
        book.save()
        messages.success(request, f'"{book.title}" updated!')
        return redirect('book_management')
    return render(request, 'library/book_edit.html', {
        'book': book, 'categories': categories
    })


@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'"{title}" deleted.')
    return redirect('book_management')

#Member management

@login_required
def member_management(request):
    query    = request.GET.get('q', '')
    students = Student.objects.all()
    if query:
        students = students.filter(
            Q(full_name__icontains=query) |
            Q(student_id__icontains=query) |
            Q(email__icontains=query)
        )
    return render(request, 'library/member_management.html', {
        'students': students,
        'query':    query,
    })


@login_required
def member_add(request):
    if request.method == 'POST':
        full_name  = request.POST.get('full_name', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        email      = request.POST.get('email', '').strip()
        phone      = request.POST.get('phone', '').strip()

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, f'Student ID "{student_id}" already exists.')
            return redirect('member_management')

        Student.objects.create(
            full_name=full_name,
            student_id=student_id,
            email=email,
            phone=phone
        )
        messages.success(request, f'"{full_name}" registered successfully!')
    return redirect('member_management')


@login_required
def member_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.full_name  = request.POST.get('full_name', '').strip()
        student.student_id = request.POST.get('student_id', '').strip()
        student.email      = request.POST.get('email', '').strip()
        student.phone      = request.POST.get('phone', '').strip()
        student.save()
        messages.success(request, f'"{student.full_name}" updated successfully!')
        return redirect('member_management')
    return render(request, 'library/member_edit.html', {'student': student})


@login_required
def member_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.full_name
        student.delete()
        messages.success(request, f'"{name}" removed.')
    return redirect('member_management')