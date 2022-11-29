from django.shortcuts import render, redirect
from .models import Phone
from datetime import datetime
from django.http import HttpResponseNotFound


def index(request):
    return redirect('catalog')


def show_catalog(request):
    template = 'catalog.html'
    sort = request.GET.get('sort')
    phones = Phone.objects.all()
    if sort:
        if sort == 'name':
            phones = phones.order_by('name')
        elif sort == 'min_price':
            phones = phones.order_by('price')
        elif sort == 'max_price':
            phones = phones.order_by('-price')
    context = {'phones': phones, 'sort': sort}
    return render(request, template, context)


def show_product(request, slug):
    template = 'product.html'
    items = Phone.objects.all().filter(slug=slug)[:1]
    if not len(items):
        return HttpResponseNotFound()
    phone = items.get()
    context = {
        'phone': {
            'name': phone.name,
            'price': phone.price,
            'image': phone.image,
            'release_date': datetime.combine(phone.release_date, datetime.min.time()).strftime('%d.%m.%Y'),
            'lte_exists': phone.lte_exists,
            'slug': phone.slug
        }
    }
    return render(request, template, context)
