from django.urls import path
from . import views

urlpatterns = [
    path('',              views.home,      name='home'),
    path('login/',        views.login_view,     name='login'),
    path('logout/',       views.logout_view,    name='logout'),
    path('books/',        views.books,          name='books'),
    path('dashboard/',    views.dashboard,      name='dashboard'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('book-management/',                     views.book_management, name='book_management'),
    path('book-management/add/',                 views.book_add,        name='book_add'),
    path('book-management/edit/<int:pk>/',       views.book_edit,       name='book_edit'),
    path('book-management/delete/<int:pk>/',     views.book_delete,     name='book_delete'),
]

