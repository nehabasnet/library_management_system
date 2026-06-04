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
        title    = request.POST.get('title', '').strip()
        author   = request.POST.get('author', '').strip()
        isbn     = request.POST.get('isbn', '').strip()
        quantity = request.POST.get('quantity', 1)
        desc     = request.POST.get('description', '').strip()
        cat_id   = request.POST.get('category')
        new_cat  = request.POST.get('new_category', '').strip()

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
            category=category, available=True
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
        cat_id = request.POST.get('category')
        if cat_id:
            book.category = get_object_or_404(Category, id=cat_id)
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