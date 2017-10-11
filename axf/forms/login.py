from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=12,#最大长度
                               min_length=6, #最小长度
                               required=True,#必填项
                               error_messages={"required":"账号不能为空","invalid":"格式错误"},#错误提醒
                                widget=forms.TextInput(attrs={"class":"c"}),#表单类型为input文本输入框
                                )

    passwd = forms.CharField(max_length=16,
                             min_length=6,
                             widget=forms.PasswordInput
                             )