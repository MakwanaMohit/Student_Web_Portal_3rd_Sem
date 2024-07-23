from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from captcha.fields import CaptchaField
import random ,string
from .utils import *

class Student_register(forms.Form):
    email = forms.EmailField()
    captcha = CaptchaField()
class Student_login(forms.Form):
    enrollment_number = forms.CharField(max_length=12,required=True)
    password = forms.CharField(required=True,widget=forms.PasswordInput)
    captcha = CaptchaField()

class Student_result(forms.Form):
    captcha = CaptchaField()
