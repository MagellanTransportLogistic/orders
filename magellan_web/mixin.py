from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.base import ContextMixin
from django.http import JsonResponse
from opened_orders.models import OrderUserProfile, OrderUserRole


class UserIsAdminCheckMixin(View):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, request, *args, **kwargs):
        return super(UserIsAdminCheckMixin, self).dispatch(request, *args, **kwargs)


class UserIsModeratorCheckMixin(View):
    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            return super(UserIsModeratorCheckMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseNotAllowed(request.method)


class UserLoginCheckMixin(View):
    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            return super(UserLoginCheckMixin, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseNotAllowed(request.method)


class OrdersUserLoginCheckMixin(View):
    @method_decorator(user_passes_test(lambda u: u.is_authenticated))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_active:
            profile = OrderUserProfile.objects.get(user_id=request.user.id)
            if profile:
                profile_access = OrderUserRole.objects.filter(uuid=profile.role_id_id).first()
                if profile_access:
                    if profile_access.have_access:
                        return super(OrdersUserLoginCheckMixin, self).dispatch(request, *args, **kwargs)

        return HttpResponseNotAllowed(request.method)


class BaseClassContextMixin(ContextMixin):
    title = ''

    def get_context_data(self, **kwargs):
        context = super(BaseClassContextMixin, self).get_context_data(**kwargs)
        context['title'] = self.title
        return context
