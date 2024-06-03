import datetime
import json
import uuid

# Create your models here.
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import UserProfile
from main.models import City


class OrderState(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="Идентификатор")
    name = models.CharField(max_length=64, unique=True, null=False, verbose_name='Наименование')
    order = models.IntegerField(default=1, unique=True, null=False, verbose_name='Порядок сортировки')
    is_processing_order = models.BooleanField(default=False, verbose_name='В работе')
    is_closed_order = models.BooleanField(default=False, verbose_name='Закрыт')

    def __str__(self):
        return self.name

    @staticmethod
    def fill_initial_data():
        def_states = [
            {
                "uuid": "92380e35-3eca-4e96-93b4-f849258478a4",
                "name": "Новый",
                "order": 1,
                "is_processing_order": False,
                "is_closed_order": False
            },
            {
                "uuid": "4c17c84c-1a87-4bdc-8fa2-ec594996ac1c",
                "name": "В работе",
                "order": 2,
                "is_processing_order": True,
                "is_closed_order": False
            },
            {
                "uuid": "7ece91d8-107a-446d-852f-c4422d35dab9",
                "name": "Завершен",
                "order": 3,
                "is_processing_order": False,
                "is_closed_order": True
            },
            {
                "uuid": "b6c0c66d-6702-49ed-82ab-2c2a988e5773",
                "name": "Отменен",
                "order": 4,
                "is_processing_order": False,
                "is_closed_order": True
            },
        ]
        for data in def_states:
            s = OrderState(**data)
            s.save()

    class Meta:
        db_table = 'opened_orders_status'
        verbose_name = "Статусы заявок"
        verbose_name_plural = "Статусы заявок"


class OrderUserRole(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, db_column='uuid', editable=False)
    name = models.CharField(verbose_name='Имя роли', max_length=64, unique=True, db_column='name')
    have_access = models.BooleanField(verbose_name='Доступ к системе заявок', default=True, db_column='have_access')
    can_take_orders = models.BooleanField(verbose_name='Принимает заявки', default=False, db_column='can_take_orders')
    can_close_orders = models.BooleanField(verbose_name='Закрывает заявки', default=False, db_column='can_close_orders')

    def __str__(self):
        return f'{self.name}'

    @staticmethod
    def fill_initial_data():
        def_profiles = [
            {
                "uuid": "07bd03f0-7f93-46dd-9e5e-395387949e57",
                "name": "Нет доступа",
                "have_access": False,
                "can_take_orders": False,
                "can_close_orders": False
            },
            {
                "uuid": "5b86954a-7501-49de-9c1a-569d7e1a015b",
                "name": "Базовый доступ",
                "have_access": True,
                "can_take_orders": False,
                "can_close_orders": False
            },
            {
                "uuid": "dd32aab4-104b-454b-b96b-b99dc790b92e",
                "name": "Прием заявок",
                "have_access": True,
                "can_take_orders": True,
                "can_close_orders": False
            },
            {
                "uuid": "780cbaa3-de03-458e-b676-1cefb34e1791",
                "name": "Закрытие заявок",
                "have_access": True,
                "can_take_orders": True,
                "can_close_orders": True
            },
        ]
        for data in def_profiles:
            p = OrderUserRole(**data)
            p.save()

    class Meta:
        db_table = 'order_user_role'
        verbose_name = "Роли"
        verbose_name_plural = "Роли"


class OrderUserOrganization(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, db_column='uuid', editable=False)
    name = models.CharField(max_length=128, verbose_name='Наименование', unique=True)

    @staticmethod
    def fill_initial_data():
        def_organizations = [
            {
                "uuid": "0cff60d6-e91b-49a9-aa26-1aa944b95ae6",
                "name": "Организация по умолчанию",
                "chief": None
            },
        ]
        for data in def_organizations:
            p = OrderUserOrganization(**data)
            p.save()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'order_user_organization'
        verbose_name = "Организации/Филиалы"
        verbose_name_plural = "Организации/Филиалы"
        ordering = ['name']


class OrderUserDepartment(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, db_column='uuid', editable=False)
    name = models.CharField(max_length=128, verbose_name='Наименование')
    organization = models.ForeignKey(OrderUserOrganization, on_delete=models.CASCADE, db_column='organization',
                                     verbose_name='Организация/Филиал', default='0cff60d6-e91b-49a9-aa26-1aa944b95ae6')

    @staticmethod
    def fill_initial_data():
        def_departments = [
            {
                "uuid": "c9940d97-0bdc-4d89-8808-7a1c57572816",
                "name": "Подразделение по умолчанию",
                "organization": OrderUserOrganization.objects.get(uuid='0cff60d6-e91b-49a9-aa26-1aa944b95ae6'),
                "chief": None
            },
        ]
        for data in def_departments:
            p = OrderUserDepartment(**data)
            p.save()

    def __str__(self):
        return f'{self.name} ({self.organization})'

    class Meta:
        db_table = 'order_user_department'
        verbose_name = "Подразделения"
        verbose_name_plural = "Подразделения"


class OrderUserProfile(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, db_column='uuid', editable=False)
    user_id = models.OneToOneField(User, unique=True, null=False, db_index=True, on_delete=models.CASCADE,
                                   db_column='user_id')
    role_id = models.ForeignKey(OrderUserRole, on_delete=models.CASCADE, verbose_name='Роль', db_column='role_uuid')
    department = models.ForeignKey(OrderUserDepartment, on_delete=models.CASCADE, db_column='department',
                                   default='c9940d97-0bdc-4d89-8808-7a1c57572816')

    def __str__(self):
        return f'{self.user_id.last_name} {self.user_id.first_name} ({self.department.name})'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):

        if created:
            if OrderUserOrganization.objects.count() == 0:
                OrderUserOrganization.fill_initial_data()
            if OrderUserDepartment.objects.count() == 0:
                OrderUserDepartment.fill_initial_data()
            if OrderUserRole.objects.count() == 0:
                OrderUserRole.fill_initial_data()
                OrderState.fill_initial_data()
            profile = OrderUserRole.objects.get(uuid='07bd03f0-7f93-46dd-9e5e-395387949e57')
            OrderUserProfile.objects.create(user_id=instance, role_id=profile)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()

    class Meta:
        db_table = 'order_user_profile'
        verbose_name = "Профили доступа"
        verbose_name_plural = "Профили доступа"


class OpenedOrder(models.Model):
    DIVISION = 'Отдел'
    DEPARTMENT = 'Филиал'
    COMPANY = 'Компания'

    VISIBILITY_CHOICES = (
        (DIVISION, 'Отдел'),
        (DEPARTMENT, 'Филиал'),
        (COMPANY, 'Компания'),
    )

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name='Идентификатор')
    number = models.BigIntegerField(db_column='number', verbose_name='Номер заявки', editable=False,
                                    default=0)
    visibility = models.CharField(verbose_name='Пол', choices=VISIBILITY_CHOICES, blank=True, max_length=16,
                                  default=DIVISION)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания', db_index=True)
    author = models.ForeignKey(OrderUserProfile, on_delete=models.CASCADE, verbose_name='Автор',
                               db_column='profile_uuid', related_name='opened_orders_profile_uuid')
    editor = models.ForeignKey(OrderUserProfile, on_delete=models.CASCADE, verbose_name='Редактор',
                               db_column='editor_uuid', related_name='opened_orders_editor_uuid')
    state = models.ForeignKey(OrderState, on_delete=models.CASCADE, verbose_name='Статус заявки',
                              db_column='state_uuid')
    load_date = models.DateTimeField(verbose_name="Дата погрузки")
    unload_date = models.DateTimeField(verbose_name='Дата выгрузки')
    load_city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город погрузки',
                                  related_name='opened_orders_lc', db_column='load_city')
    upload_city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город выгрузки',
                                    related_name='opened_orders_uc', db_column='upload_city')
    ext_upload_city = models.ForeignKey(City, on_delete=models.DO_NOTHING, verbose_name='Дополнительная выгрузка',
                                        related_name='opened_orders_ec', db_column='ext_upload_city', blank=True,
                                        null=True)
    vehicle_type = models.CharField(max_length=256, verbose_name='Тип автомобиля')
    cargo_type = models.CharField(max_length=256, verbose_name='Характер груза', default='')
    cargo_weight = models.FloatField(verbose_name='Вес груза', default=0)
    cargo_ext_params = models.CharField(max_length=256, verbose_name='Параметры для нестандартных грузов', default='')
    cargo_price_fixed = models.FloatField(verbose_name='Стоимость перевозки фиксированная', default=0)
    cargo_price_floated = models.FloatField(verbose_name='Стоимость перевозки ориентировочная', default=0)
    comments = models.TextField(verbose_name='Комментарий', default='', null=True)

    def __str__(self):
        return f'{self.created_at} {self.author} {self.load_city} -> {self.upload_city}, {self.cargo_price_fixed}'

    @staticmethod
    def get_new_number():
        prefix = int(datetime.date.today().strftime('%Y%m%d'))
        last_number = OpenedOrder.objects.filter(number__gte=int(f'{prefix}0001')).aggregate(Max('number'))[
                          'number__max'] or 0
        suffix = int(str(last_number).replace(str(prefix), ''))
        suffix = suffix + 1
        suffix = str(suffix).zfill(4)
        return int(f'{prefix}{suffix}')

    class Meta:
        db_table = 'opened_orders_list'
        indexes = [models.Index(fields=['number'], name='number')]
        verbose_name = "Открытые заявки"
        verbose_name_plural = "Открытые заявки"
        # ordering = ('created_at',)


class OrderHistory(models.Model):
    values_list = [
        'author',
        'editor',
        'state',
        'load_date',
        'unload_date',
        'load_city',
        'upload_city',
        'ext_upload_city',
        'cargo_type',
        'cargo_weight',
        'cargo_ext_params',
        'cargo_price_fixed',
        'cargo_price_floated',
        'comments'
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Идентификатор')
    record_date = models.DateTimeField(auto_now=True, editable=False, verbose_name='Дата записи')
    order_uuid = models.ForeignKey(OpenedOrder, on_delete=models.CASCADE, verbose_name='Заявка', db_column='order_uuid')
    order_state = models.ForeignKey(OrderState, on_delete=models.CASCADE, verbose_name='Статус заявки',
                                    db_column='order_state')
    detailed_data = models.TextField(verbose_name='Детальная информация')

    def __str__(self):
        return f'{self.record_date}: {self.order_uuid}'

    def as_json(self):
        data = {}
        for value in self.values_list:
            obj = getattr(self.order_uuid, value)
            if isinstance(obj, OrderUserProfile):
                obj = obj.user_id.id
            if isinstance(obj, OrderState):
                obj = str(obj.uuid)
            if isinstance(obj, OpenedOrder):
                obj = str(obj.uuid)
            if isinstance(obj, City):
                obj = str(obj.uuid)
            if isinstance(obj, datetime.datetime):
                obj = obj.strftime('%Y-%m-%d %H:%M:%S')

            data[value] = obj

        return json.dumps(data, ensure_ascii=False, indent=4)

    @receiver(post_save, sender=OpenedOrder)
    def create_record(sender, instance, created, **kwargs):
        obj = OrderHistory.objects.create(order_uuid=instance, record_date=instance.created_at,
                                          order_state=instance.state, detailed_data={})
        obj.detailed_data = obj.as_json()
        obj.save()

    class Meta:
        db_table = 'opened_orders_history'
        verbose_name = "Открытые заявки: История"
        verbose_name_plural = "Открытые заявки: История"
