import datetime

import django_filters
from django.forms import DateInput
from django_filters import *
from django_filters.fields import DateRangeField
from django_filters.widgets import RangeWidget, DateRangeWidget

from .models import *


class OrderFilter(django_filters.FilterSet):
    state_id = ModelChoiceFilter(queryset=OrderState.objects.all().order_by('order'),
                                 label='Статус', empty_label='---Статус---')

    def __init__(self, *args, **kwargs):
        super(OrderFilter, self).__init__(*args, **kwargs)
        self.form.fields['state_id'].widget.attrs['id'] = 'state_id'
        self.form.fields['state_id'].widget.attrs['class'] = 'form-select'
        self.form.fields['state_id'].widget.attrs[
            'style'] = 'margin-right: 10px; min-width: 150px; max-width: 400px'
        self.form.fields['state_id'].widget.attrs['selected'] = 'Статус'

    class Meta:
        model = OpenedOrder
        fields = {'state'}
