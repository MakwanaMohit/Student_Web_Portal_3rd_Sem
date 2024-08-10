from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from captcha.fields import CaptchaField
from django.core.validators import MinLengthValidator,MaxLengthValidator

from Student_app.models import Student
import random ,string
# from .utils import *

class Student_register(forms.Form):
    email = forms.EmailField()
    captcha = CaptchaField()
class Student_login(forms.Form):
    enrollment_number = forms.CharField(max_length=12,required=True)
    password = forms.CharField(required=True,widget=forms.PasswordInput)
    captcha = CaptchaField()

class Student_result(forms.Form):

    captcha = CaptchaField()

class Student_result_enroll(forms.Form):
    enrollment = forms.CharField(max_length=12,required=True)
    captcha = CaptchaField()

class StudentUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    stu_DOB = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
        required=True
    )
    stu_parents_mobile_num = forms.CharField(required=True,min_length=10,max_length=10)
    stu_mobile_num = forms.CharField(required=True,min_length=10,max_length=10)
    adhar_no = forms.CharField(required=True,min_length=12,max_length=12)
    gender = forms.ChoiceField(required=True,choices=Student.Gender.choices)
    profile_picture = forms.ImageField(required=False)  # Optional if not required
    stu_address = forms.CharField(required=True, widget=forms.Textarea)
    class Meta:
        model = Student
        fields = ['profile_picture','adhar_no', 'stu_DOB', 'gender', 'stu_mobile_num', 'stu_parents_mobile_num', 'stu_address']

