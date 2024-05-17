from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm


class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Имя пользователя'
        self.fields['password'].widget.attrs['placeholder'] = 'Пароль'
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control py-2'


class UserPasswordChangeForm(SetPasswordForm):
    """
    Форма изменения пароля
    """

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы
        """
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })
