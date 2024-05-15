from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
import re
from django.urls import re_path
from django.views.static import serve
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from .views import *

app_name = 'main'
app_label = 'main'

urlpatterns = \
    [
        path('', IndexPageFormView.as_view(), name='index'),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
