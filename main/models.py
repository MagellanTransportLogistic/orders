import uuid

# Create your models here.
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import UserProfile


class City(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Идентификатор')
    code = models.CharField(max_length=12, verbose_name='Код')
    name = models.CharField(max_length=256, blank=False, null=False, default='Москва',
                            verbose_name='Наименование')
    full_name = models.CharField(max_length=512, unique=True, blank=False, null=False, default='Нет',
                                 verbose_name='Полное наименование')
    creator = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='Автор записи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'main_city'
        verbose_name = "Города"
        verbose_name_plural = "Города"
        indexes = [models.Index(fields=['name'])]
