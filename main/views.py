from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, ListView, TemplateView
from django.views.generic.edit import BaseFormView, UpdateView

from magellan_web.mixin import *
from .models import *


# from .forms import *
# from .filters import *

# Create your views here.
class IndexPageFormView(BaseClassContextMixin, TemplateView):
    title = 'Компания Магеллан'
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexPageFormView, self).get_context_data(**kwargs)
        return context
