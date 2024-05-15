import json

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from opened_orders.models import *
from users.models import *
from main.models import *

from magellan_web.settings import BASE_DIR

FILE_PATH = BASE_DIR / 'main/json/'


def read_json(path):
    with open(FILE_PATH / path, 'rb') as f:
        return json.loads(f.read())


class Command(BaseCommand):
    def handle(self, *args, **options):

        if User.objects.all().count() == 0:
            print('Creating default users...')
            User.objects.all().delete()
            User.objects.create(
                id=1, username='dark',
                password='pbkdf2_sha256$720000$422UTGSM14RyIbOM0ybtEu$xDPnuKt8FwG748ZxIvN/0YtLiLKsvRIArlPyEZDKHDE=',
                email='a.kovalenko@magellan.ru', is_staff=True, is_active=True, is_superuser=True)

        if City.objects.all().count() == 0:
            print('Creating default locations...')

            obj = City(uuid='00000000-0000-0000-0000-000000000000', name='Нет', full_name='Нет', creator_id=1)
            if City.objects.filter(name='Нет').count() == 0:
                obj.save()

            data = read_json('locations.json')
            for city in data['cities']:
                city['creator_id'] = 1
                city['name'] = str(city['name']).rstrip().lstrip()
                obj = City(**city)
                if City.objects.filter(name=city['name']).count() == 0:
                    obj.save()

        if OrderUserDepartment.objects.all().count() < 2:
            print('Creating departments...')
            data = read_json('departments.json')
            for department in data['departments']:
                obj = OrderUserDepartment(**department)
                obj.save()
