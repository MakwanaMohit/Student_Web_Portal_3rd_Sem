from Student_Website.settings import  EMAIL_HOST_USER,EMAIL_PORT,EMAIL_HOST,EMAIL_HOST_PASSWORD,EMAIL_USE_TLS
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.template.loader import render_to_string ,get_template
from django.template.defaulttags import url
from django.shortcuts import render,redirect
from django.core.mail import EmailMessage
from django.http import HttpResponse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .models import Student as appstu
from .models import Student_Marks
from user.models import Student,User
from main.models import Sub_Syllabus
from .forms import Student_register,Student_login
from .utils import *
from django.urls import reverse
import smtplib
import random,string
from weasyprint import HTML,CSS


# Create your views here.

# @login_required(login_url='/student/signin')
def home(request):
    from Student_app.utils import generate_fake_students
    # generate_fake_students()
    return render(request,"Student_app\home.html",{'user':request.user})

def signup(request):
    if request.method == 'POST':
        try:
            enroll = request.POST['username']
            username = None
            request.session['enrollment'] = None
        except:
            username = request.session.get('enrollment', None)
            enroll = username
            form = Student_register(request.POST)
        request.session['enrollment'] = None

        if valid_username(enroll) and enroll == username and username is not None:
            if form.is_valid() :
                student_model = appstu.objects.get(stu_enroll=username)
                email = request.POST['email']
                password = generate_password()
                st = Student()
                st.username = username
                st.email = email
                st.first_name = student_model.stu_name
                st.password = password
                st.save()

                # emal part is here
                subject = 'password for student account'
                current_url = get_current_site(request)
                message_body = render_to_string('Student_app/password_mail.html',{
                    'enroll' : enroll,
                    'domain' : current_url.domain,
                    'password' : password,
                    'forgot' : False
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
                return redirect('student signin')
            else:
                form = Student_register()

                request.session['enrollment'] = username
                email = request.POST['email']
                messages.error(request,'Please enter a correct captcha for login ')
                return render(request, "Student_app\signup.html", {"form": form,'url_name':reverse('student signup'),'email':email})
        else:
            if valid_enroll(enroll):
                if user_is_exits(enroll):
                    messages.error(request,'this user is arlady exits in system please use different enrollment')
                    return render(request, "Student_app\signup.html",{'url_name':reverse('student signup'),'signup_enroll':True})
                else:
                    form = Student_register()

                    request.session['enrollment'] = enroll
                    return render(request, "Student_app\signup.html", {"form": form,'url_name':reverse('student signup')})
            else:
                messages.error(request,'this is not a valid enrollment ! Please enter a valid enrollment')
                return render(request, "Student_app\signup.html",{'url_name':reverse('student signup'),'signup_enroll':True})

    return render(request, "Student_app\signup.html",{'url_name':reverse('student signup'),'signup_enroll':True })
    # return render(request, "Student_app\signup_enroll.html",{'url_name':reverse('student signup'),'signup_enroll':True ,'form':form})


@login_not_required_restric
def signin(request):
    if request.method == "POST":
        form = Student_login(request.POST)
        if form.is_valid():
            username = request.POST['enrollment_number']
            pass1= request.POST['password']
            user = authenticate(username = username, password = pass1)
            if user is not None:
                if user.role == User.Role.STUDENT:
                    login(request,user)
                    next = request.GET.get('next',None)
                    if next:
                        return redirect(next)

                    return redirect('student home')
                else:
                    messages.error(request, "You logged in wrong Page with these id and password please login in this page")
                    if user.role == User.Role.ADMIN:
                        return redirect('admin:index')
                    elif user.role == User.Role.FACULTY:
                        return redirect('faculty signin')

            else:
                form = Student_login()
                messages.error(request,'Please Enter a valid username or password for login')
                return render(request, "Student_app\signin.html", {
                    'form': form,
                    'enrollment_value': request.POST['enrollment_number']
                })


        else:
            form = Student_login()
            messages.error(request,'Please enter a valid captcha ')
            return render(request, "Student_app\signin.html", {
                'form': form,
                'enrollment_value':request.POST['enrollment_number'],
                'password': request.POST['password']
            })

    form = Student_login()
    return render(request,"Student_app\signin.html",{
        'form':form,

    })

def signout(request):
    logout(request)
    messages.success(request,"Signed Out Succeesfully ")
    return render(request,'Student_app/signout.html')

def forgot(request):
    if request.method == 'POST':
        try:
            enroll = request.POST['username']
            username = None
            request.session['enrollment'] = None
        except:
            username = request.session.get('enrollment', None)
            enroll = username
            form = Student_register(request.POST)
        request.session['enrollment'] = None

        if valid_enroll(username) and user_is_exits(enroll) and username is not None:
            if form.is_valid():
                student = Student.objects.get(username=username)
                email = request.POST['email']
                if email != student.email:

                    form = Student_register()
                    request.session['enrollment'] = username
                    messages.error(request,f'email is dosen\'t matching with email that we have \n Please try again or contact your superfaculty to change the email')
                    return render(request, "Student_app\signup.html",
                                  {"form": form, 'url_name': reverse('student forgot'),'forgot':True})

                password = generate_password()
                student.password = password
                student.save()
                # emal part is here
                subject = 'reset password for student account'
                current_url = get_current_site(request)
                message_body = render_to_string('password_mail.html', {
                    'enroll': enroll,
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
                messages.success(request,f'your new password is send to you register email {student.email[:7]}********* \n')
                return redirect('student signin')
            else:
                form = Student_register()
                request.session['enrollment'] = username
                messages.error(request,'Please enter a correct captcha for login ')
                return render(request, "Student_app\signup.html", {"form": form,'url_name':reverse('student forgot'),'forgot':True,'email':request.POST['email']})
        else:
            if valid_enroll(enroll):
                use = user_is_exits(enroll)
                if use:
                    form = Student_register()

                    request.session['enrollment'] = enroll
                    messages.error(request,f'Enter the email starts with {use.email[:7]}********* that given by you in the registration time')
                    return render(request, "Student_app\signup.html", {"form": form,'url_name':reverse('student forgot'),'forgot':True})
                else:
                    messages.error(request,'this user is not exits in system please use different enrollment')
                    return render(request, "Student_app\signup.html",
                              {'url_name': reverse('student forgot'),'signup_enroll': True,'forgot':True})
            else:
                messages.error(request,'this is not a valid enrollment ! Please enter a valid enrollment')
                return render(request, "Student_app\signup.html",
                              {'url_name': reverse('student forgot'), 'signup_enroll': True,'forgot':True})

    return render(request, "Student_app\signup.html",
                  {'url_name': reverse('student forgot'),'signup_enroll': True,'forgot':True})



@login_required(login_url='/student/signin')
def result(request):
    if request.method == 'POST':
        sem = request.POST.get('sem',None)
        enroll =  request.user.username
        stu = Student_Marks.objects.filter(stu_sem = sem,stu_enroll=enroll)
        if len(stu)<1:
            messages.error(request,'this is a wrong sem or the result for these sem is not available\n please reenter the sem')

            return redirect('student result')
        first = stu[0]
        sub = None

        if request.POST.get('pdf'):

            pdf = get_template("Student_app/pdf_result.html")
            pdf_render = pdf.render({
            'student_marks':stu,
            'first_mark':first,
            'student':first.student,
            'subject':first.subject,
            'sem':True,
            'pdf':False
            })
            custom_style = CSS(string='@page { size: A4; } body { transform: scale(1.1); }')
            # Generate PDF using WeasyPrint
            pdf_file = HTML(string=pdf_render).write_pdf(stylesheets=[custom_style])

            # Create an HTTP response with PDF content
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'{first.student.stu_name}filename="result.pdf"'
            return response
        return render(request,"Student_app/result.html",{
            'student_marks':stu,
            'first_mark':first,
            'student':first.student,
            'subject':first.subject,
            'sem':True,
            'pdf':True
        })
    sem = []
    try:
        student = appstu.objects.get(stu_enroll=request.user.username)
        marks = Student_Marks.objects.get_queryset().filter(student=student)
        for mark in marks:
            se = mark.stu_sem
            if se not in sem:sem.append(se)
    except Exception as e:
        messages.error(request, "marks entry for you is not done yet please try after your result date declare")
        return redirect(reverse('student home'))
    if not sem:
        messages.error(request,"marks entry for you is not done yet please try after your result date declare")
        return redirect(reverse('student home'))
    return render(request,'Student_app/result.html',{'url_name':reverse('student result'),'sem_information':sem})






def seeder(request):
    if request.method == 'POST':
        se = request.POST['selection1']
        if se == '2':
            Student(username='hii2',password='hello',is_staff=True,is_superuser=True).save()
            return HttpResponse('records makes sussecfully')
        else:
            # return HttpResponse('records makes sussecfully')
            from faker import Faker
            import random

            # Create a Faker instance
            fake = Faker()

            # Initialize an empty list to store student records
            student_records = []

            # Generate 30 random student records
            for _ in range(150):
                name = fake.name()
                dob = fake.date_of_birth(minimum_age=5, maximum_age=18)  # Generate DOB for students between 5 and 18 years old
                address = fake.address()
                mobile = fake.phone_number()
                parent_mobile = fake.phone_number()

                student_record = [name, dob, address, mobile[:10], parent_mobile[:10]]
                student_records.append(student_record)

            enr = {3: 226340316001,
            1: 236340316001,
            5: 216340316001}
            for stu in student_records:
                sem = random.choice([1,3,5])
                enroll = enr[sem]
                enr[sem]+= 1
                b_code = str(random.randint(1, 45))
                appstu.objects.create(
                stu_name= stu[0],
                stu_enroll = enroll,
                stu_sem = sem,
                stu_DOB = stu[1],
                # stu_branch_code = random.choice(list(branchlist.keys())),
                stu_branch_code = '16',
                stu_mobile_num = stu[3],
                stu_parents_mobile_num = stu[4],
                stu_address = stu[2]
                )
                enroll += 1

            return HttpResponse('records makes sussecfully')
    messages.error(request,'this is not correct')
    return render(request,'seed.html')