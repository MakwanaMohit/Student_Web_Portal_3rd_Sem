from django.template.loader import render_to_string
from Student_Website.settings import  EMAIL_HOST_USER,EMAIL_PORT,EMAIL_HOST,EMAIL_HOST_PASSWORD,EMAIL_USE_TLS
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render,redirect
from django.core.mail import EmailMessage
from django.http import HttpResponse,Http404
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from Student_app.forms import Student_login
from .models import Faculty_Records
from Student_app.utils import generate_password
from user.models import Faculty,User
from main.models import Sub_Syllabus
from django.urls import reverse
import smtplib
import random,string
from .models import *
from django.conf import settings
from django.conf.urls.static import static
from .forms import Faculty_register,Faculth_login
from .utitls import login_not_required_restric,user_is_exits

# Create your views here.

def home(request):
    user = request.user
    if user.is_authenticated and user.role == User.Role.FACULTY:
        return redirect(reverse('admin:index'))
    return render(request,'faculty/home.html')
def signup(request):
    email = ''
    if request.method == 'POST':
        form = Faculty_register(request.POST)
        email = request.POST.get('email',None)
        if form.is_valid():
            if not user_is_exits(email):
                faculty = Faculty_Records.objects.filter(email=email).first()
                if faculty:
                    fac = Faculty()
                    password = generate_password()
                    # emal part is here
                    fac.username = email
                    fac.password = password
                    fac.email = email
                    fac.first_name = faculty.fac_name
                    fac.is_staff = True
                    fac.save()
                    # Get the group named 'Faculty'
                    faculty_group = Group.objects.get(name='Faculty')

                    # Add the user to the group
                    faculty_group.user_set.add(fac)

                    faculty.user = fac
                    faculty.save()
                    subject = 'password for Faculty account'
                    current_url = get_current_site(request)
                    message_body = render_to_string('password_mail.html', {
                        'email': email,
                        'domain': current_url.domain,
                        'password': password,
                        'forgot': False
                    })
                    Email = EmailMessage(
                        subject,
                        message_body,
                        "Student Management Website",
                        [email]
                    )
                    Email.fail_silently = True
                    Email.send()
                    messages.success(request, "Your Account has been successfully created.")
                    return redirect('faculty signin')
                else:
                    messages.error(request,'This email is not registered. Please enter correct email OR contact administrator.')
            else:
                messages.error(request,'User with this email is arlady exists. Reset Your password if you don\'t remember')
                return redirect(reverse('faculty signin'))
        else:
            messages.error(request,'Please Enter Valid Captcha')

    form = Faculty_register()
    return render(request, "faculty/signup.html",{"form": form,'url_name':reverse('faculty signup'),'email':email})
@login_not_required_restric
def signin(request):
    if request.method == "POST":
        form = Faculth_login(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            pass1= request.POST['password']
            user = authenticate(username = email, password = pass1)
            if user is not None:
                if user.role == User.Role.FACULTY:
                    login(request,user)
                    next = request.GET.get('next',None)
                    if next:
                        return redirect(next)

                    return redirect('faculty home')
                else:
                    messages.error(request, "You logged in wrong Page with these id and password please login in this page")
                    if user.role == User.Role.ADMIN:
                        return redirect('admin:index')
                    elif user.role == User.Role.STUDENT:
                        return redirect('student signin')

            else:
                form = Faculth_login()
                messages.error(request,'Please Enter a valid username or password for login')
                return render(request, "faculty\signin.html", {
                    'form': form,
                    'email': email
                })


        else:
            form = Faculth_login()
            messages.error(request,'Please enter a valid captcha ')
            return render(request, "faculty\signin.html", {
                'form': form,
                'email':request.POST.get('email',""),
                'password': request.POST['password']
            })

    form = Faculth_login()
    return render(request,"faculty\signin.html",{
        'form':form,

    })

def forgot(request):
    email = ''
    if request.method == 'POST':
        form = Faculty_register(request.POST)
        email = request.POST.get('email',None)
        if form.is_valid():
            fac = user_is_exits(email)
            if fac:
                password = generate_password()
                fac.password = password
                # fac.password = "hello"
                fac.save()
                subject = 'reset password for faculty account'
                current_url = get_current_site(request)
                message_body = render_to_string('password_mail.html', {
                    'email': email,
                    'domain': current_url.domain,
                    'password': password,
                    'forgot': True
                })
                Email = EmailMessage(
                    subject,
                    message_body,
                    "Student Management Website",
                    [email]
                )
                Email.fail_silently = True
                Email.send()
                messages.success(request, "password reset successfully and new password has been sent to your email")
                return redirect('faculty signin')
            else:
                messages.error(request,'User not exists with this email. Signup here')
                return redirect(reverse('faculty signup'))
        else:
            messages.error(request,'Please Enter Valid Captcha')

    form = Faculty_register()
    return render(request, "faculty/signup.html",{"form": form,'url_name':reverse('faculty forgot'),'email':email,'forgot':True})


def signout(request):
    logout(request)
    return redirect('faculty signin')


def dashbord(request):
    return render(request, "faculty/dashbord.html")