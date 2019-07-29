from django import forms
from django.forms import widgets
from blog.models import *
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS


class User(forms.Form):
    user = forms.CharField(max_length=32,
                           label='用户名',
                           error_messages={'required': '用户名不能为空'},
                           widget=widgets.TextInput(attrs={'class': 'form-control'},)
                           )
    pwd = forms.CharField(max_length=32,
                          label='密码',
                          error_messages={'required': '密码不能为空'},
                          widget=widgets.PasswordInput(attrs={'class': 'form-control'},))
    e_pwd = forms.CharField(max_length=32,
                            label='确认密码',
                            error_messages={'required': '密码确认不能为空'},
                            widget=widgets.PasswordInput(attrs={'class': 'form-control'},))
    email = forms.EmailField(max_length=32,
                             label='邮箱',
                             error_messages={'required': '邮箱不能为空'},
                             widget=widgets.EmailInput(attrs={'class': 'form-control'},))

    def clean_user(self):   # 用户名钩子
        user = self.cleaned_data.get('user')
        ret = UserInfo.objects.filter(username=user).first()
        if not ret:     # 没被注册过
            return user
        else:
            raise ValidationError('该用户名已被注册！')

    def clean(self):    # 全局钩子，判断密码是否一致
        pwd = self.cleaned_data.get('pwd')
        e_pwd = self.cleaned_data.get('e_pwd')
        if pwd and e_pwd:   # 如果有一个没输入，就不必判断密码是否一致了
            if pwd == e_pwd:
                return self.cleaned_data
            else:
                raise ValidationError('两次密码不一致！')



