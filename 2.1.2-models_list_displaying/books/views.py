from django.shortcuts import render
from .models import Book
from datetime import datetime
from django.http import HttpResponseNotFound


def books_view(request, pub_date=None):
    template = 'books/books_list.html'
    date_filter = datetime.strptime(pub_date, '%Y-%m-%d').date() if pub_date else None
    items = Book.objects.all() if date_filter is None else Book.objects.filter(pub_date=date_filter)
    if not len(items):
        return HttpResponseNotFound()
    books = [{
        'name': book.name,
        'author': book.author,
        'pub_date': datetime.combine(book.pub_date, datetime.min.time()).strftime('%Y-%m-%d')
    } for book in items]
    context = {'books': books}
    if date_filter:
        date_list = list(Book.objects.order_by('pub_date').values_list('pub_date', flat=True).distinct())
        date_index = date_list.index(date_filter)
        if date_index > 0:
            context['date_prev'] = datetime.combine(date_list[date_index - 1], datetime.min.time()).strftime('%Y-%m-%d')
        if date_index + 1 < len(date_list):
            context['date_next'] = datetime.combine(date_list[date_index + 1], datetime.min.time()).strftime('%Y-%m-%d')
    return render(request, template, context)
