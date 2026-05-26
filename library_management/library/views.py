from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from .models import Book


def home(request):
    return render(request, 'library/index.html')


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            return render(request, 'library/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'library/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')



def books(request):

    query = request.GET.get('q')

    books = Book.objects.all().order_by('category__name')

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(category__name__icontains=query)
        )

    return render(request, 'library/books.html', {
        'books': books
    })
