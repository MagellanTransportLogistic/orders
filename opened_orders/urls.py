from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
import re
from django.urls import re_path
from django.views.static import serve
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from .views import *

app_name = 'opened_orders'
app_label = 'opened_orders'

urlpatterns = \
    [
        path('orders/', IndexPageFormView.as_view(), name='list'),
        path('orders/modify/<pk>', OrderModify.as_view(), name='order_edit'),
        path('orders/update', OrderModify.as_view(), name='order_update'),
        path('orders/create', OrderCreate.as_view(), name='order_create'),
        path('orders/search_city', SearchCity.as_view(), name='search_city'),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
