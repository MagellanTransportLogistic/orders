# Generated by Django 5.0.6 on 2024-06-03 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('opened_orders', '0008_alter_openedorder_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderuserdepartment',
            name='chief',
        ),
        migrations.RemoveField(
            model_name='orderuserorganization',
            name='chief',
        ),
    ]
