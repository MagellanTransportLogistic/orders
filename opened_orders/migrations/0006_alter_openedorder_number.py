# Generated by Django 5.0.6 on 2024-05-21 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opened_orders', '0005_alter_openedorder_number_openedorder_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openedorder',
            name='number',
            field=models.BigIntegerField(db_column='number', default=0, editable=False, verbose_name='Номер заявки'),
        ),
    ]
