from django import forms
from django.forms import widgets


class UserForm(forms.Form):
    username = forms.CharField(max_length=18, min_length=3, label='用户名',
                               widget=widgets.TextInput(attrs={'class': 'form-control'}), error_messages={
            'max_length': '最长18位', 'min_length': '最短3位', 'required': '该字段必填'
        })
    password = forms.CharField(max_length=18, min_length=3, label='密码',
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}), error_messages={
            'max_length': '最长18位', 'min_length': '最短3位', 'required': '该字段必填'
        })
    re_password = forms.CharField(max_length=18, min_length=3, label='确认密码',
                                  widget=widgets.PasswordInput(attrs={'class': 'form-control'}), error_messages={
            'max_length': '最长18位', 'min_length': '最短3位', 'required': '该字段必填'
        })
    email = forms.EmailField(label='邮箱', widget=widgets.EmailInput(attrs={'class': 'form-control'}),
                             error_messages={'required': '该字段必填', 'invalid': '格式不正确'})
    phone = forms.CharField(max_length=18, min_length=3, label='手机号',
                            widget=widgets.TextInput(attrs={'class': 'form-control'}), error_messages={
            'max_length': '最长18位', 'min_length': '最短3位', 'required': '该字段必填'
        })

    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password != re_password:
            self.add_error('re_password', '两次密码不一致')
        return self.cleaned_data
