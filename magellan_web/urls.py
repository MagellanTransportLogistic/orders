from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.urls import path, include

urlpatterns = [
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('opened_orders/', include('opened_orders.urls')),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]
