# Generated by Django 5.0.6 on 2024-06-03 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opened_orders', '0010_alter_orderuserdepartment_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='openedorder',
            options={'verbose_name': 'Открытые заявки', 'verbose_name_plural': 'Открытые заявки'},
        ),
        migrations.AlterModelOptions(
            name='orderuserorganization',
            options={'ordering': ['name'], 'verbose_name': 'Организации/Филиалы', 'verbose_name_plural': 'Организации/Филиалы'},
        ),
        migrations.AlterField(
            model_name='openedorder',
            name='number',
            field=models.BigIntegerField(db_column='number', default=0, editable=False, verbose_name='Номер заявки'),
        ),
        migrations.AlterField(
            model_name='openedorder',
            name='visibility',
            field=models.CharField(blank=True, choices=[('Отдел', 'Отдел'), ('Филиал', 'Филиал'), ('Компания', 'Компания')], default='Отдел', max_length=16, verbose_name='Пол'),
        ),
    ]
