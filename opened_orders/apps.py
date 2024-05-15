from django.apps import AppConfig


class OpenedOrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'opened_orders'
    verbose_name = 'Открытые заявки'
