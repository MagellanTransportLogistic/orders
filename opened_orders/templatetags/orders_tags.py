from datetime import datetime

from django import template

from main.models import City
from opened_orders.models import OrderUserRole, OrderUserProfile

register = template.Library()


@register.filter
def can_view_orders(_object, user):
    try:
        if user.id is not None:
            profile = OrderUserProfile.objects.get(user_id=user)
            if profile.role_id.have_access:
                return True
            else:
                return False
        else:
            return False
    except Exception as E:
        return False


@register.simple_tag(name='convert_date')
def get_date_time(date_time):
    if isinstance(date_time, datetime):
        return date_time.strftime("%d.%m.%Y %H:%M:%S")
    return 'Неизвестная дата'


@register.simple_tag(name='convert_date_only')
def get_date_only(date_time):
    if isinstance(date_time, datetime):
        return date_time.strftime("%d.%m.%Y")
    return 'Неизвестная дата'


@register.simple_tag(name='get_city_name')
def get_city_name_by_id(city_uuid):
    return City.objects.get(uuid=city_uuid).name
