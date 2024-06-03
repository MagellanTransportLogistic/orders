import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.forms import Form
from .models import *


class CustomChoiceField(forms.ModelChoiceField):

    def validate(self, value):
        return True

    def clean(self, value):
        return value


class FormOpenedOrder(forms.ModelForm):
    uuid = forms.CharField(max_length=64, disabled=True, label='Идентификатор')
    number = forms.IntegerField(disabled=True, label='Номер заявки')
    visibility = forms.ChoiceField(choices=OpenedOrder.VISIBILITY_CHOICES, label='Видимость заявки', )
    created_at = forms.DateTimeField(disabled=True, label='Дата создания')
    author = forms.ModelChoiceField(queryset=OrderUserProfile.objects.all(), disabled=True, label='Автор',
                                    empty_label=None)
    editor = forms.ModelChoiceField(queryset=OrderUserProfile.objects.all(), disabled=True, label='Редактор',
                                    empty_label=None)
    state = forms.ModelChoiceField(queryset=OrderState.objects.filter(order__gte=0).order_by('order'), label='Статус',
                                   empty_label=None)
    load_date = forms.DateField(input_formats=['%d.%m.%Y'], label='Дата погрузки')
    unload_date = forms.DateField(input_formats=['%d.%m.%Y'], label='Дата разгрузки')
    load_city = CustomChoiceField(queryset=City.objects.filter(name=''), widget=forms.TextInput,
                                  label='Город погрузки', empty_label=None)
    upload_city = CustomChoiceField(queryset=City.objects.filter(name=''), widget=forms.TextInput,
                                    label='Город разгрузки', empty_label=None)
    ext_upload_city = CustomChoiceField(queryset=City.objects.filter(name=''), widget=forms.TextInput,
                                        label='Дополнительная разгрузка', empty_label=None)
    vehicle_type = forms.CharField(max_length=256, label='Тип транспорта')
    cargo_type = forms.CharField(max_length=256, label='Тип груза')
    cargo_weight = forms.FloatField(min_value=0.0, label='Вес груза')
    cargo_ext_params = forms.CharField(max_length=256, label='Дополнительные параметры груза')
    cargo_price_fixed = forms.FloatField(min_value=0.0, label='Фиксированная стоимость')
    cargo_price_floated = forms.FloatField(min_value=0.0, label='Ориентировочная стоимость')
    comments = forms.CharField(max_length=512, label='Комментарий')

    def __init__(self, *args, **kwargs):
        _placeholders = {
            'load_city': 'Введите город погрузки',
            'ext_upload_city': 'Введите промежуточный город выгрузки',
            'upload_city': 'Введите город выгрузки',
            'vehicle_type': 'Введите тип транспорта',
            'cargo_type': 'Укажите тип груза',
            'cargo_ext_params': 'Введите доп. параметры груза',
            'cargo_weight': 'Вес груза (в тоннах)',
            'cargo_price_fixed': 'Цена (руб.)',
            'cargo_price_floated': 'Цена (руб.)',
            'comments': 'Комментарий к заявке'
        }
        _initials = {
            'created_at': datetime.datetime.now(),
            'load_date': datetime.datetime.now(),
            'unload_date': datetime.datetime.now() + datetime.timedelta(7),
            'uuid': str(uuid.uuid4()),
            'cargo_type': 'Неизвестно',
            'vehicle_type': 'Неизвестно',
            'cargo_ext_params': 'Нет',
            'ext_upload_city': 'Нет',
            'comments': 'Нет',
            'cargo_weight': 0.0,
            'cargo_price_fixed': 0.0,
            'cargo_price_floated': 0.0,
        }

        super(FormOpenedOrder, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['id'] = field_name

            if _placeholders.get(field_name, None) is not None:
                field.widget.attrs['placeholder'] = _placeholders[field_name]
            if _initials.get(field_name, None) is not None:
                field.initial = _initials[field_name]

            if isinstance(field, (forms.CharField, forms.FloatField)):
                field.widget.attrs['class'] = 'form-control small'
                field.widget.attrs['autocomplete'] = 'off'

            if isinstance(field, (forms.ModelChoiceField, forms.ChoiceField)):
                field.widget.attrs['class'] = 'form-select small'
                field.widget.attrs['autocomplete'] = 'off'

            if isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
                field.widget.attrs['type'] = 'checkbox'

            if isinstance(field, (forms.DateField, forms.DateTimeField, forms.TimeField)):
                field.widget.attrs['class'] = 'datepicker form-control'
                field.widget.attrs['readonly'] = True

    class Meta:
        model = OpenedOrder
        fields = '__all__'


class FormOpenedOrderModify(FormOpenedOrder):

    def __init__(self, *args, **kwargs):
        super(FormOpenedOrderModify, self).__init__(*args, **kwargs)
        self.fields['created_at'].initial = OpenedOrder.objects.get(uuid=self.instance.uuid).created_at
        # self.fields['load_city'].initial = City.objects.get(uuid=self.instance.load_city).full_name

    def clean_state(self):
        new_data = self.cleaned_data['state']
        old_data = self.instance.state

        # Отменен - можно ставить с любого статуса.
        if new_data.order == 4:
            return new_data

        if new_data.order == 1:
            return new_data

        # Новый статус должен отличаться.
        if not (new_data.order - old_data.order == 1) or (old_data.order - new_data.order == 1):
            raise ValidationError('Разрешается только последовательная смена статусов!')

        return new_data


class FormOpenedOrderCreate(FormOpenedOrder):
    state = forms.ModelChoiceField(queryset=OrderState.objects.filter(order=1).order_by('order'), label='Статус',
                                   empty_label=None)

    def __init__(self, *args, **kwargs):
        super(FormOpenedOrderCreate, self).__init__(*args, **kwargs)
