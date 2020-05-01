from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import (authenticate, get_user_model, password_validation,)
from .models import configurationRules, ColorRange
import re

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

# Configuration Rule Form
class configurationRulesForm(forms.ModelForm):
    class Meta:
        model = configurationRules
        fields = '__all__'
        exclude = [
            'user'
        ]
        
        labels = {
            'header': "Header Name"
        }
        
        help_texts = {
            'color' : "Color Range for fetched results"
        }
        widgets={
            'header': forms.TextInput(attrs={
                'autocomplete' : "off",
                'placeholder' : "Header Name ( or Category)",
                'class':"form-control"
            }),
            
            'name': forms.TextInput(attrs={
                'autocomplete' : "off",
                'placeholder' : "Stats rules name",
                'class':"form-control"
            }),
            
            'source': forms.Select(attrs={
                'autocomplete' : "off",
                'placeholder' : "Source",
                'class':"form-control"
            }),

            'source_query': forms.TextInput(attrs={
                'autocomplete' : "off",
                'placeholder' : "SQL Query/Linux Shell Command",
                'class':"form-control"
            }),
            
            'resultDataType': forms.Select(attrs={
                'autocomplete' : "off",
                'placeholder' : "Result Data Type",
                'class':"form-control"
            }),
            
            'color': forms.SelectMultiple(attrs={
                'autocomplete' : "off",
                'placeholder' : "Color Range",
                'class':"form-control"
            }),
            
            'Schedule_Run_Config': forms.TextInput(attrs={
                'autocomplete' : "off",
                'placeholder' : "Schedule Run Config",
                'class':"form-control"
            }),

            'emailID': forms.EmailInput(attrs={
                'autocomplete' : "off",
                'placeholder' : "Email",
                'class':"form-control"
            }),
        }
        

        
# Result Color Range Form
class ColorRangeForm(forms.ModelForm):
    range = forms.CharField(max_length = 20,
                            label = "Results Range",
                            help_text = "For Example: 10<resutls<20 or results > 10 or results < 10 . Use 'results' variable to define reange.",
                            widget = forms.TextInput(
                                attrs = {
                                    'autocomplete' : "off",
                                    'placeholder' : "Results Range",
                                    'class':"form-control"
                                }
                            )  
                        )
    class Meta:
        model = ColorRange
        fields = [
            'color',
        ]
        
        help_texts = {
            'color' : "Color Range for fetched results",
        }
        
        widgets = {
            'color': forms.Select(attrs={
                'autocomplete' : "off",
                'placeholder' : "Color",
                'class':"form-control"
            }),
        }
        
    def clean_range(self):
        A = []
        range_data = self.cleaned_data.get("range")
        if "results" not in range_data:
            raise ValidationError("There is no 'results' variable in \"{query}\"".format(query=range_data))
        elif "results" not in range_data.split(" ") :
            raise ValidationError("User spaces between words in  \"{query}\"".format(query=range_data))
        range_data = range_data.split(" ")
        for i in range(range_data.count("")):
            range_data.remove("")
        range_data = " ".join(range_data)
        A.append(re.compile("results < \d+"))
        A.append(re.compile("results <= \d+"))
        A.append(re.compile("results > \d+"))
        A.append(re.compile("results >= \d+"))
        A.append(re.compile("results = \d+"))
        A.append(re.compile("\d+ < results < \d+"))
        A.append(re.compile("\d+ < results <= \d+"))
        A.append(re.compile("\d+ < results > \d+"))
        A.append(re.compile("\d+ < results >= \d+"))
        A.append(re.compile("\d+ < results = \d+"))
        A.append(re.compile("\d+ <= results < \d+"))
        A.append(re.compile("\d+ <= results <= \d+"))
        A.append(re.compile("\d+ <= results > \d+"))
        A.append(re.compile("\d+ <= results >= \d+"))
        A.append(re.compile("\d+ <= results = \d+"))
        A.append(re.compile("\d+ > results < \d+"))
        A.append(re.compile("\d+ > results <= \d+"))
        A.append(re.compile("\d+ > results > \d+"))
        A.append(re.compile("\d+ > results >= \d+"))
        A.append(re.compile("\d+ > results = \d+"))
        A.append(re.compile("\d+ >= results < \d+"))
        A.append(re.compile("\d+ >= results <= \d+"))
        A.append(re.compile("\d+ >= results > \d+"))
        A.append(re.compile("\d+ >= results >= \d+"))
        A.append(re.compile("\d+ >= results = \d+"))
        A.append(re.compile("\d+ = results < \d+"))
        A.append(re.compile("\d+ = results <= \d+"))
        A.append(re.compile("\d+ = results > \d+"))
        A.append(re.compile("\d+ = results >= \d+"))
        A.append(re.compile("\d+ = results = \d"))
        for i in A:
            if i.match(range_data):
                return range_data
        raise ValidationError("Invalid \"{query}\"".format(query=range_data))