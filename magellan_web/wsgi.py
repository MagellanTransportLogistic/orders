"""
WSGI config for magellan_web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""
import logging
import os
from threading import Thread
from time import sleep
from datetime import datetime, timedelta
from django.core.wsgi import get_wsgi_application

from opened_orders.models import OpenedOrder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'magellan_web.settings')

application = get_wsgi_application()


def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target=function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()

    return decorator


@start_new_thread
def check_order_state():
    print(f'Loaded Orders visibility checker.')
    while True:
        time_offset = datetime.now() - timedelta(hours=2)
        order_list = OpenedOrder.objects.filter(created_at__lte=time_offset).filter(
            visibility__in=[OpenedOrder.DIVISION, OpenedOrder.DEPARTMENT])
        for order in order_list:
            print(f'Found orders with private state: {order_list.count()}')
            order.visibility = OpenedOrder.COMPANY
            order.save()
        sleep(10)


check_order_state()
