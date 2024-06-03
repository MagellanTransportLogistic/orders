import uuid

# Create your models here.
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    MALE = 'Мужской'
    FEMALE = 'Женский'
    HIDDEN = 'Не указан'

    GENDER_CHOICES = (
        (MALE, 'Мужской'),
        (FEMALE, 'Женский'),
        (HIDDEN, 'Не указан')
    )

    userid = models.OneToOneField(User, unique=True, null=False, db_index=True, on_delete=models.CASCADE)
    user_uuid = models.UUIDField(max_length=64, unique=True, null=False, db_index=True, verbose_name='Идентификатор',
                                 default=uuid.uuid4)
    creation_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    birthday = models.DateField(verbose_name='Дата рождения', null=False, default='2001-01-01')
    about = models.TextField(verbose_name='О себе', blank=True, null=True)
    gender = models.CharField(verbose_name='Пол', choices=GENDER_CHOICES, blank=True, max_length=16,
                              default=HIDDEN)
    phone_number = models.CharField(max_length=16, verbose_name='Номер телефона')

    def __str__(self):
        return f'{self.userid.last_name} {self.userid.first_name}, ' \
               f'email: {self.userid.email}, ' \
               f'создан: {self.creation_datetime}'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(userid=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()

    class Meta:
        db_table = 'auth_profile'
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class Systems(models.Model):
    system_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    system_name = models.CharField(max_length=128, unique=True, null=False, db_index=True)

    def __str__(self):
        return self.system_name

    class Meta:
        db_table = 'auth_systems'
        verbose_name = "Информационные системы"
        verbose_name_plural = "Информационные системы"


class UserSystem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    user_id = models.ForeignKey(UserProfile, db_column='user_id', verbose_name='Профиль', default=uuid.uuid4,
                                on_delete=models.CASCADE)
    user_system = models.ForeignKey(Systems, db_column='system_uuid', verbose_name='Система', null=False,
                                    on_delete=models.CASCADE)
    user_uuid = models.UUIDField(db_column='user_system_uuid', db_index=True,
                                 verbose_name='Идентификатор пользователя в системе')

    def __str__(self):
        return f'{self.user_id.userid.username}, ' \
               f'Система: {self.user_system.system_name}'

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=('user_id', 'user_system'), name="%(app_label)s_%(class)s_unique")
        ),
        db_table = 'auth_user_systems'
        verbose_name = "Интеграционные данные профилей"
        verbose_name_plural = "Интеграционные данные профилей"
