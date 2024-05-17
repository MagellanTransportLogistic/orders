from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
from .views import *
from main.views import *

app_name = 'users'

urlpatterns = \
    [
        path('users/', IndexPageFormView.as_view(), name='index'),
        path('login/', UserLoginView.as_view(), name='login'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
