from django.contrib import admin
from .models import *

admin.site.register(OrderState)
admin.site.register(OrderUserRole)
admin.site.register(OrderUserProfile)
admin.site.register(OrderHistory)
admin.site.register(OpenedOrder)
admin.site.register(OrderUserOrganization)
admin.site.register(OrderUserDepartment)
