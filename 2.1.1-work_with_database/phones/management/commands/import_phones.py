import csv

from django.core.management.base import BaseCommand
from phones.models import Phone
from datetime import datetime
from django.template.defaultfilters import slugify


class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with open('phones.csv', 'r') as file:
            phones = list(csv.DictReader(file, delimiter=';'))

        for phone in phones:
            Phone.objects.create(
                name=phone.get('name'),
                price=float(phone.get('price')),
                image=phone.get('image'),
                release_date=datetime.strptime(phone.get('release_date'), '%Y-%m-%d').date(),
                lte_exists=(phone.get('lte_exists').lower() in ['true', '1', 'yes']),
                slug=slugify(phone.get('name'))
            )
