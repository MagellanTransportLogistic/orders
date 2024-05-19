import json
import os

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


city_locations = ['locations.json', 'locations_add.json']


class Command(BaseCommand):
    def handle(self, *args, **options):

        if User.objects.all().count() == 0:
            print('Создание пользователей по умолчанию...')
            User.objects.all().delete()
            User.objects.create(
                id=1, username='dark',
                password='pbkdf2_sha256$720000$422UTGSM14RyIbOM0ybtEu$xDPnuKt8FwG748ZxIvN/0YtLiLKsvRIArlPyEZDKHDE=',
                email='a.kovalenko@magellan.ru', is_staff=True, is_active=True, is_superuser=True, first_name='Андрей',
                last_name='Коваленко')

            role = OrderUserProfile.objects.get(user_id=1)
            role.role_id = OrderUserRole.objects.get(uuid='780cbaa3de03458eb6761cefb34e1791')
            role.save()

            User.objects.create(
                id=2, username='kerleada',
                password='pbkdf2_sha256$720000$onAjV8vIe6LYNqZ6m6vPVY$LGEJgQNSJLV3bJh2iUCJWvJcZiRqMJ4NolfiVDXWIjs=',
                email='e.morin@magellan.ru', is_staff=True, is_active=True, is_superuser=True, first_name='Егор',
                last_name='Морин')

            role = OrderUserProfile.objects.get(user_id=2)
            role.role_id = OrderUserRole.objects.get(uuid='780cbaa3de03458eb6761cefb34e1791')
            role.save()

        print('Создание данны справочника "Города"...')
        obj = City(uuid='00000000-0000-0000-0000-000000000000', code='0000000000000', name='Нет', full_name='Нет',
                   creator_id=1)
        if City.objects.filter(uuid='00000000-0000-0000-0000-000000000000').count() == 0:
            obj.save()

        for file in city_locations:
            print(f'Обработка данных файла: {file}')
            if os.path.exists(FILE_PATH / file):
                data = read_json(file)
                print(f'Чтение данных файла: {file}')
                for city in data['cities']:
                    city['creator_id'] = 1
                    city['name'] = str(city['name']).rstrip().lstrip()
                    obj = City(**city)
                    try:
                        _get_city = City.objects.get(full_name=city['full_name'])
                    except City.DoesNotExist:
                        print(f"Создаю новый город: {city['full_name']}")
                        obj.save()
            else:
                print(f'Файл: {file} не обнаружен. Игнорирую.')

        if OrderUserDepartment.objects.all().count() < 2:
            print('Создание подразделений...')
            data = read_json('departments.json')
            for department in data['departments']:
                obj = OrderUserDepartment(**department)
                obj.save()

        if os.path.exists(FILE_PATH / 'profiles.json'):
            data = read_json(FILE_PATH / 'profiles.json')
            for user in data['profiles']:
                obj = User(**user)
                if User.objects.filter(username=user['username']).count() == 0:
                    obj.is_active = True
                    obj.save()
                for role in OrderUserProfile.objects.all():
                    role.role_id = OrderUserRole.objects.get(uuid='780cbaa3de03458eb6761cefb34e1791')
                    role.save()
