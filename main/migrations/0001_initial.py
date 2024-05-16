# Generated by Django 5.0.4 on 2024-05-14 13:07

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='Идентификатор')),
                ('code', models.CharField(max_length=12, verbose_name='Код')),
                ('name', models.CharField(default='Москва', max_length=256, verbose_name='Наименование')),
                ('full_name', models.CharField(default='Нет', max_length=512, unique=True, verbose_name='Полное наименование')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.userprofile', verbose_name='Автор записи')),
            ],
            options={
                'verbose_name': 'Города',
                'verbose_name_plural': 'Города',
                'db_table': 'main_city',
                'indexes': [models.Index(fields=['name'], name='main_city_name_2abeaa_idx')],
            },
        ),
    ]