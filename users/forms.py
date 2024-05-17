from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django import forms


class LoginForms(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        _placeholders = {

        }
        _initial = {

        }

        super(LoginForms, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['id'] = field_name

            if _placeholders.get(field_name, None) is not None:
                field.widget.attrs['placeholder'] = _placeholders[field_name]

            if isinstance(field, (forms.CharField, forms.FloatField, forms.ModelChoiceField)):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['autocomplete'] = 'off'

            if isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
                field.widget.attrs['type'] = 'checkbox'

            if isinstance(field, (forms.DateField, forms.DateTimeField, forms.TimeField)):
                field.widget.attrs['class'] = 'datepicker form-control'
                field.widget.attrs['readonly'] = True


class UserLoginForm(AuthenticationForm, LoginForms):

    def __init__(self, *args, **kwargs):
        _placeholders = {
            'username': 'Имя пользователя',
            'password': 'Пароль',
        }
        super(UserLoginForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('username', 'password')


class UserPasswordChangeForm(SetPasswordForm, LoginForms):
    """
    Форма изменения пароля
    """

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы
        """
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')