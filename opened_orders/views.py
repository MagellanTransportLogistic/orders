import datetime
from copy import deepcopy

from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, ListView, TemplateView, CreateView
from django.views.generic.edit import BaseFormView, UpdateView

from magellan_web import settings
from magellan_web.mixin import *
from .models import *
from .forms import *
from .filters import OrderFilter


# from .forms import *
# from .filters import *

# Create your views here.
class IndexPageFormView(BaseClassContextMixin, ListView):
    title = 'Компания Магеллан: Активные заявки'
    template_name = 'opened_orders/orders.html'
    model = OpenedOrder
    paginate_by = 50

    def __init__(self, **kwargs):
        super(IndexPageFormView, self).__init__(**kwargs)
        self.filter_set = None
        self.object = None
        self.is_ajax = False

    def get_queryset(self):
        qs = OpenedOrder.objects.all()
        data = self.request.GET
        if data == {}:
            data = {'state_id': '92380e35-3eca-4e96-93b4-f849258478a4'}
        self.filter_set = OrderFilter(data, queryset=qs)
        return self.filter_set.qs

    def get_context_data(self, **kwargs):
        context = super(IndexPageFormView, self).get_context_data(**kwargs)
        context['filter'] = self.filter_set
        return context


class SearchCity(ListView):

    def __init__(self, **kwargs):
        super(SearchCity, self).__init__(**kwargs)
        self.object = None
        self.is_ajax = False

    def get(self, request, *args, **kwargs):
        self.is_ajax = True if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else False

        name_param = request.GET.get('name', None)
        if name_param is not None:
            if settings.DATABASES.get('default')['ENGINE'] == 'mssql':
                data = City.objects.filter(name__contains=name_param).order_by('name').values('uuid', 'full_name')[
                       :500]
            else:
                data = City.objects.filter(Q(name__iregex=name_param)).order_by('name').values('uuid', 'full_name')[
                       :500]
            if self.is_ajax:
                return JsonResponse(list(data), safe=False)
            return JsonResponse(list(data), safe=False)


class OrderCreate(BaseClassContextMixin, CreateView):
    title = 'Создать заявку'
    model = OpenedOrder
    form_class = FormOpenedOrderCreate
    template_name = 'opened_orders/order_create.html'
    success_url = reverse_lazy('opened_orders:list')

    def __init__(self, **kwargs):
        super(OrderCreate, self).__init__(**kwargs)
        self.object = None
        self.is_ajax = False

    def get_context_data(self, **kwargs):
        context = super(OrderCreate, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):

        self.is_ajax = True if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else False

        if self.is_ajax:
            try:
                request.POST._mutable = True
                request.POST['load_city'] = City.objects.get(full_name=request.POST['load_city'])
                request.POST['ext_upload_city'] = City.objects.get(full_name=request.POST['ext_upload_city'])
                request.POST['upload_city'] = City.objects.get(full_name=request.POST['upload_city'])
                request.POST['author'] = OrderUserProfile.objects.get(uuid=request.POST['author'])
                request.POST['editor'] = OrderUserProfile.objects.get(user_id=request.user.id)

                form = self.form_class(data=request.POST, initial={
                    'author': request.POST['author'],
                    'editor': request.POST['editor']
                })

                if form.is_valid():
                    self.object = form.save()
                    return JsonResponse(
                        {'result': 1, 'object': self.object.uuid,
                         'data': '<html></html>'})
                else:
                    return JsonResponse({'result': -1, 'data': render_to_string(
                        'opened_orders/errors.html',
                        {'errors': form.errors})})
            except ValueError as E:
                return JsonResponse({'result': -1, 'data': render_to_string('opened_orders/errors.html',
                                                                            {'errors': E.args})})
            except City.DoesNotExist:
                return JsonResponse({'result': -1, 'data': render_to_string('opened_orders/errors.html', context={
                    'errors': 'Удостоверьтесь что все адреса введены корректно!',
                })})

        return redirect(self.success_url)


class OrderModify(BaseClassContextMixin, UpdateView):
    title = 'Редактировать заявку'
    model = OpenedOrder
    form_class = FormOpenedOrderModify
    template_name = 'opened_orders/order_modify.html'
    success_url = reverse_lazy('opened_orders:list')

    def __init__(self, **kwargs):
        super(OrderModify, self).__init__(**kwargs)
        self.object = None
        self.is_ajax = False

    def get_form(self, form_class=None):
        form = super(OrderModify, self).get_form(form_class=form_class)
        return form

    def get_context_data(self, **kwargs):
        context = super(OrderModify, self).get_context_data(**kwargs)
        context['item'] = self.object
        return context

    def post(self, request, *args, **kwargs):

        self.is_ajax = True if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else False

        if self.is_ajax:
            try:
                request.POST._mutable = True
                request.POST['created_at'] = OpenedOrder.objects.get(uuid=request.POST.get('uuid')).created_at
                request.POST['load_city'] = City.objects.get(full_name=request.POST['load_city'])
                request.POST['ext_upload_city'] = City.objects.get(full_name=request.POST['ext_upload_city'])
                request.POST['upload_city'] = City.objects.get(full_name=request.POST['upload_city'])

                editor = OrderUserProfile.objects.get(user_id=request.user.id)
                form = self.form_class(data=request.POST,
                                       instance=self.model.objects.get(uuid=request.POST['uuid']),
                                       initial={'editor': editor})

                if form.is_valid():
                    self.object = form.save()
                    return JsonResponse(
                        {'result': 1, 'object': self.object.uuid,
                         'data': render_to_string('opened_orders/inc/order_line.html', {'item': self.object})})
                else:
                    return JsonResponse({'result': -1, 'data': render_to_string('opened_orders/errors.html',
                                                                                {'errors': form.errors})})
            except ValueError as E:
                return JsonResponse({'result': -1, 'data': render_to_string('opened_orders/errors.html',
                                                                            {'errors': E.args})})

        return redirect(self.success_url)
