from datetime import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from magellan_web.mixin import BaseClassContextMixin, UserLoginCheckMixin
from .forms import *
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import PasswordChangeView


class UserLogoutView(BaseClassContextMixin, UserLoginCheckMixin, LogoutView):
    template_name = "main/index.html"


class UserLoginView(BaseClassContextMixin, LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy("main:index")
    title = 'Авторизация'


class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    """
    Изменение пароля пользователя
    """
    form_class = UserPasswordChangeForm
    template_name = 'users/password_change.html'
    success_url = reverse_lazy("main:index")
    success_message = 'Ваш пароль был успешно изменён!'

    def get_context_data(self, **kwargs):
        context = super(UserPasswordChangeView, self).get_context_data(**kwargs)
        context['title'] = 'Изменение пароля на сайте'
        return context
