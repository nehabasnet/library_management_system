from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Book, Category, ContactInfo, Student, IssueBook, ContactMessage, Reservation
from django.http import JsonResponse
from django.core.paginator import Paginator 

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
    query       = request.GET.get('q')
    category_id = request.GET.get('category')
    books       = Book.objects.all().order_by('category__name')
    categories  = Category.objects.all()

    if category_id:
        books = books.filter(category_id=category_id)
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(category__name__icontains=query)
        )

    paginator = Paginator(books, 12)  
    page      = request.GET.get('page')
    books     = paginator.get_page(page)

    return render(request, 'library/books.html', {
        'books':             books,
        'categories':        categories,
        'selected_category': category_id,
    })
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)

    has_pending_reservation = Reservation.objects.filter(
        book=book,
        status='pending'
    ).exists()

    return render(request, 'library/book_detail.html', {
        'book': book,
        'has_pending_reservation': has_pending_reservation,
    })

def reserve_book(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        student_id = request.POST.get('student_id', '').strip()
        email = request.POST.get('email', '').strip()

        # Check if this person has already reserved this book
        existing_reservation = Reservation.objects.filter(
            book=book,
            student_id=student_id,
            status='pending'
        ).exists()

        if existing_reservation:
            messages.warning(
                request,
                f'You have already reserved "{book.title}".'
            )
            return redirect('book_detail', pk=book.pk)

        Reservation.objects.create(
            book=book,
            full_name=full_name,
            student_id=student_id,
            email=email,
        )

        messages.success(
            request,
            f'Reservation submitted successfully for "{book.title}"!'
        )

        return redirect('book_detail', pk=book.pk)

    return render(
        request,
        'library/reserve_book.html',
        {'book': book}
    )


@login_required
def reservation_management(request):
    reservations = Reservation.objects.select_related('book').all()
    return render(request, 'library/reservation_management.html', {'reservations': reservations})


@login_required
def reservation_fulfill(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.status = 'fulfilled'
    reservation.save()
    messages.success(request, f'Reservation for "{reservation.book.title}" marked as fulfilled.')
    return redirect('reservation_management')


@login_required
def reservation_cancel(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.status = 'cancelled'
    reservation.save()
    messages.success(request, f'Reservation for "{reservation.book.title}" cancelled.')
    return redirect('reservation_management')

def contact(request):
    contact = ContactInfo.objects.first()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name, email=email, subject=subject, message=message,
            )
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'error': 'All fields are required.'}, status=400)

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
    paginator = Paginator(books, 10)  
    page = request.GET.get('page')       
    books = paginator.get_page(page)
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
    paginator = Paginator(students, 10)  
    page      = request.GET.get('page')
    students  = paginator.get_page(page)

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

#Issue and Return Books

from datetime import date, timedelta

@login_required
def issue_book(request):
    students = Student.objects.all()
    books    = Book.objects.filter(quantity__gt=0)

    if request.method == 'POST':
        student_id = request.POST.get('student')
        book_id    = request.POST.get('book')
        student    = get_object_or_404(Student, pk=student_id)
        book       = get_object_or_404(Book, pk=book_id)

        # Check stock
        if book.quantity < 1:
            messages.error(request, f'"{book.title}" is out of stock.')
            return redirect('issue_book')

        # Check if student already has this book
        already = IssueBook.objects.filter(
            student=student, book=book, return_date__isnull=True
        ).exists()
        if already:
            messages.error(request, f'{student.full_name} already has "{book.title}" issued.')
            return redirect('issue_book')

        # Create issue record
        due = date.today() + timedelta(days=14)
        IssueBook.objects.create(
            student=student,
            book=book,
            due_date=due
        )

        # Decrease stock
        book.quantity -= 1
        if book.quantity == 0:
            book.available = False
        book.save()

        messages.success(request, f'"{book.title}" issued to {student.full_name}. Due: {due.strftime("%B %d, %Y")}')
        return redirect('issue_book')

    today   = date.today()
    records = IssueBook.objects.filter(
        return_date__isnull=True
    ).select_related('student', 'book').order_by('due_date')

    return render(request, 'library/issue_book.html', {
        'students': students,
        'books':    books,
        'records':  records,
        'today':    today,
    })


@login_required
def issued_list(request):
    today   = date.today()
    records = IssueBook.objects.filter(
        return_date__isnull=True
    ).select_related('student', 'book').order_by('due_date')
    
    paginator = Paginator(records, 10) 
    page      = request.GET.get('page')
    records   = paginator.get_page(page)

    return render(request, 'library/issued_list.html', {
        'records': records,
        'today':   today,
    })

#Return Book

@login_required
def return_book(request, pk):
    record = get_object_or_404(IssueBook, pk=pk)
    today  = date.today()

    # Calculate fine preview (NPR 5 per day)
    overdue_days = max(0, (today - record.due_date).days)
    fine_preview = overdue_days * 5

    if request.method == 'POST':
        record.return_date = today
        record.fine        = fine_preview
        record.save()

        # Restore book stock
        record.book.quantity += 1
        record.book.available = True
        record.book.save()

        if fine_preview > 0:
            messages.success(
                request,
                f'"{record.book.title}" returned by {record.student.full_name}. '
                f'Fine: NPR {fine_preview} ({overdue_days} days overdue)'
            )
        else:
            messages.success(
                request,
                f'"{record.book.title}" returned by {record.student.full_name}. No fine — returned on time!'
            )
        return redirect('issued_list')

    return render(request, 'library/return_book.html', {
        'record':       record,
        'today':        today,
        'overdue_days': overdue_days,
        'fine_preview': fine_preview,
    })

#Fine Management

# ── Fine Management (Day 7) ───────────────────────────────────────

@login_required
def fine_management(request):
    today = date.today()

    collected = IssueBook.objects.filter(
        return_date__isnull=False,
        fine__gt=0
    ).select_related('student', 'book').order_by('-return_date')

    overdue = IssueBook.objects.filter(
        return_date__isnull=True,
        due_date__lt=today
    ).select_related('student', 'book').order_by('due_date')

    pending_records = []
    for record in overdue:
        days = (today - record.due_date).days
        fine = days * 5
        pending_records.append({
            'record':       record,
            'overdue_days': days,
            'pending_fine': fine,
        })

   
    total_collected = sum(r.fine for r in collected)
    total_pending   = sum(p['pending_fine'] for p in pending_records)
    total_all       = total_collected + total_pending

    paginator = Paginator(collected, 10)
    page      = request.GET.get('page')
    collected = paginator.get_page(page)

    return render(request, 'library/fine_management.html', {
        'collected':       collected,
        'pending_records': pending_records,
        'total_collected': total_collected,
        'total_pending':   total_pending,
        'total_all':       total_all,
        'today':           today,
    })

# Book history

@login_required
def book_history(request):
    today  = date.today()
    query  = request.GET.get('q', '')
    filter_by = request.GET.get('filter', 'all')

    records = IssueBook.objects.select_related(
        'student', 'book'
    ).all().order_by('-issue_date')

    # Search
    if query:
        records = records.filter(
            Q(student__full_name__icontains=query) |
            Q(student__student_id__icontains=query) |
            Q(book__title__icontains=query)
        )

    # Filter
    if filter_by == 'returned':
        records = records.filter(return_date__isnull=False)
    elif filter_by == 'issued':
        records = records.filter(return_date__isnull=True)
    elif filter_by == 'overdue':
        records = records.filter(
            return_date__isnull=True,
            due_date__lt=today
        )

    paginator = Paginator(records, 10)
    page      = request.GET.get('page')
    records   = paginator.get_page(page)

    return render(request, 'library/book_history.html', {
        'records':   records,
        'today':     today,
        'query':     query,
        'filter_by': filter_by,
    })