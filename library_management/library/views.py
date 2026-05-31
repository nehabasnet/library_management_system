from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Book, Category, ContactInfo

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
from .models import Book

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