from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import (authenticate, get_user_model, password_validation,)

#User Login Form ................
class loginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput())

#User Registration Form...................
class registerForm(forms.ModelForm):
    password = forms.CharField(label = 'Password', widget = forms.PasswordInput(),strip=False,help_text=password_validation.password_validators_help_text_html(),)
    password2 = forms.CharField(label = 'Repeat Password', widget = forms.PasswordInput(),strip=False,help_text="Both Passwords should be same.",)
    email = forms.EmailField(label = 'Email Address', widget = forms.TextInput())
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
        ]

    #Cleaning Method for password Match..........
    def clean_password2(self):
        cd = self.cleaned_data
        if self.cleaned_data.get('password') != cd['password2']:
            raise forms.ValidationError("Passwords don't match.")
        return cd['password2']

    #Cleaning Method for Email Unique..........
    def clean(self):
        if self.cleaned_data.get('email') is None:
            raise ValidationError("Enter a valid E-mail Address")
        varEmail = self.cleaned_data.get('email').lower()
        if User.objects.filter(email = varEmail).count() != 0 :
            if not User.objects.get(email = varEmail).is_active :
                User.objects.get(email = varEmail).delete()
            else:
                raise ValidationError(self.cleaned_data.get('email') + "\tAlready Exists.")
    
#User Can Edit his profile using this Form..........................
class EditProfileForm(UserChangeForm):
    password = forms.CharField(label='', widget = forms.TextInput(attrs = {'type' : 'hidden'}))
    class Meta:
        model = User
        fields = ['username',
                  'first_name',
                  'last_name',
                  'password',
                  ]
