from django.core.paginator import Paginator
from pagination import settings as pagination_settings
from django.shortcuts import render, redirect
from django.urls import reverse
import csv


BUS_STATIONS_DATA = []
with open(pagination_settings.BUS_STATION_CSV, newline='', encoding='utf8') as file:
    BUS_STATIONS_DATA = [line for line in csv.DictReader(file)]


def index(request):
    return redirect(reverse('bus_stations'))


def bus_stations(request):
    # получите текущую страницу и передайте ее в контекст
    # также передайте в контекст список станций на странице
    paginator = Paginator(BUS_STATIONS_DATA, 10)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    context = {
        'bus_stations': page.object_list,
        'page': page,
    }
    return render(request, 'stations/index.html', context)
