from django import template
from django.contrib.auth.models import User
from opened_orders.models import OrderUserProfile

register = template.Library()


@register.simple_tag(name='user_login_name')
def get_login_full_name(user):
    if user.first_name and user.last_name:
        return ' '.join([user.first_name, user.last_name])
    return user.username


@register.simple_tag(name='user_login_name_by_id')
def get_login_full_name_by_id(user_id):
    user = User.objects.get(pk=user_id)

    if user.first_name and user.last_name:
        return ' '.join([user.first_name, user.last_name])
    return user.username


@register.simple_tag(name='user_login_name_by_user_order_uuid')
def get_login_full_name_by_user_order_uuid(user_uuid):
    order_user = OrderUserProfile.objects.get(uuid=user_uuid)
    user = order_user.user_id

    if user.first_name and user.last_name:
        return ' '.join([user.first_name, user.last_name])
    return user.username
