# Generated by Django 5.0.6 on 2024-07-01 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_city_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramBotUsers',
            fields=[
                ('user_id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('login', models.TextField()),
                ('name', models.TextField()),
                ('snils', models.CharField(max_length=32, unique=True)),
                ('role_id', models.IntegerField(default=1)),
            ],
            options={
                'verbose_name': 'Пользователи Telegram',
                'verbose_name_plural': 'Пользователи Telegram',
                'db_table': 'tgbot_users',
            },
        ),
    ]