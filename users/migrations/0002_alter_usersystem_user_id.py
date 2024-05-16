# Generated by Django 5.0.6 on 2024-05-16 09:28

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersystem',
            name='user_id',
            field=models.ForeignKey(db_column='user_id', default=uuid.uuid4, on_delete=django.db.models.deletion.CASCADE, to='users.userprofile', verbose_name='Профиль'),
        ),
    ]
