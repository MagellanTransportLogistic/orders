import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.forms import Form
from .models import *

placeholders = {
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


class CustomChoiceField(forms.ModelChoiceField):

    def validate(self, value):
        return True

    def clean(self, value):
        return value


class FormOpenedOrderModify(forms.ModelForm):
    uuid = forms.CharField(max_length=64, disabled=True, label='Идентификатор')
    created_at = forms.DateTimeField(disabled=True, label='Дата создания')
    author = forms.ModelChoiceField(queryset=OrderUserProfile.objects.all(), disabled=True, label='Автор',
                                    empty_label=None)
    editor = forms.ModelChoiceField(queryset=OrderUserProfile.objects.all(), disabled=True, label='Редактор',
                                    empty_label=None)
    state = forms.ModelChoiceField(queryset=OrderState.objects.filter(order__gte=0), label='Статус', empty_label=None)
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
        super(FormOpenedOrderModify, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['placeholder'] = placeholders.get(field_name, '')
            field.widget.attrs['name'] = field_name
            field.widget.attrs['autocomplete'] = 'off'
            if isinstance(field, forms.CharField):
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field, forms.FloatField):
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
                field.widget.attrs['type'] = 'checkbox'
            if isinstance(field, forms.DateField):
                field.widget.attrs['class'] = 'datepicker form-control'
                field.widget.attrs['id'] = field_name
                field.widget.attrs['readonly'] = True
            if isinstance(field, forms.DateTimeField):
                field.widget.attrs['class'] = 'datepicker form-control'
                field.widget.attrs['id'] = field_name
                field.widget.attrs['readonly'] = True
            if isinstance(field, forms.ModelChoiceField):
                field.widget.attrs['class'] = 'form-control'

        self.fields['created_at'].initial = OpenedOrder.objects.get(uuid=self.instance.uuid).created_at

    def clean_state(self):
        new_data = self.cleaned_data['state']
        old_data = self.instance.state
        if new_data.order - old_data.order not in [1, -1] and new_data.order != old_data.order:
            raise ValidationError('Разрешается только последовательная смена статуса.')

        return new_data

    class Meta:
        model = OpenedOrder
        fields = '__all__'


class FormOpenedOrderCreate(forms.ModelForm):
    uuid = forms.CharField(max_length=64, disabled=True, label='Идентификатор')
    created_at = forms.DateTimeField(disabled=True, label='Дата создания')
    author = forms.ModelChoiceField(queryset=OrderUserProfile.objects.all(), disabled=True, label='Автор',
                                    empty_label=None)
    editor = forms.ModelChoiceField(queryset=OrderUserProfile.objects.all(), disabled=True, label='Редактор',
                                    empty_label=None)
    state = forms.ModelChoiceField(queryset=OrderState.objects.filter(order__lte=1), label='Статус', empty_label=None)
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
        super(FormOpenedOrderCreate, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['name'] = field_name
            field.widget.attrs['placeholder'] = placeholders.get(field_name, '')
            field.widget.attrs['autocomplete'] = 'off'
            if isinstance(field, forms.CharField):
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field, forms.FloatField):
                field.widget.attrs['class'] = 'form-control'
            if isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
                field.widget.attrs['type'] = 'checkbox'
            if isinstance(field, forms.DateField):
                field.widget.attrs['class'] = 'datepicker form-control'
                field.widget.attrs['id'] = field_name
                field.widget.attrs['readonly'] = True
            if isinstance(field, forms.DateTimeField):
                field.widget.attrs['class'] = 'datepicker form-control'
                field.widget.attrs['id'] = field_name
                field.widget.attrs['readonly'] = True
            if isinstance(field, forms.ModelChoiceField):
                field.widget.attrs['class'] = 'form-control'

        self.fields['created_at'].initial = datetime.datetime.now()
        self.fields['load_date'].initial = datetime.datetime.now()
        self.fields['unload_date'].initial = datetime.datetime.now() + datetime.timedelta(7)
        self.fields['uuid'].initial = str(uuid.uuid4())
        self.fields['cargo_type'].initial = 'Неизвестно'
        self.fields['vehicle_type'].initial = 'Неизвестно'
        self.fields['cargo_ext_params'].initial = 'Нет'
        self.fields['ext_upload_city'].initial = 'Нет'
        self.fields['comments'].initial = 'Нет'
        self.fields['cargo_weight'].initial = 0.0
        self.fields['cargo_price_fixed'].initial = 0.0
        self.fields['cargo_price_floated'].initial = 0.0

    class Meta:
        model = OpenedOrder
        fields = '__all__'
