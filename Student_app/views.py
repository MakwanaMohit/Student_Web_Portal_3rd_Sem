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
from .models import Publish_Result
from user.models import Student,User
from main.models import Sub_Syllabus
from .forms import Student_register,Student_login,Student_result,Student_result_enroll
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
    publish = sorted(list(Publish_Result.objects.filter(published=True).values_list('year','session','sem','type').distinct()),reverse=True)

    return render(request,"Student_app\home.html",{'user':request.user,'results':publish})

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



def result(request):
    published = Publish_Result.objects.filter(published=True)
    Form = Student_result_enroll
    session = []
    if request.user.is_authenticated:
        Form = Student_result
        if request.user.role != User.Role.STUDENT:
            messages.error(request,'You are not a student !')
            return redirect('main home')

        stu = app_stu.objects.get(stu_enroll=request.user.username)
        marks = []
        stu_marks = Student_Marks.objects.filter(student=stu)
        for sem,mty in list(stu_marks.values_list('stu_sem','exam_type').distinct()):marks.append(f'S{sem}-{mty}')
        marks.sort(reverse=True)
        published = published.filter(id__in=marks)
    t = list(published.values_list('year','session').distinct())
    t.sort(reverse=True)
    for year,sess in t:session.append(f'{sess}-{year}')
    context = {'session':session,'form':Form()}


    if request.method == 'POST':
        sess = request.POST.get('session',session[0])
        context['curr_session'] = sess
        ses,year = sess.split('-')
        e_type = request.POST.get('exam-type',None)
        context['ctype'] = e_type
        ty = published.filter(year=year, session=ses).values_list('sem', 'type').distinct().order_by('sem')
        type = []
        for sem, typ in ty: type.append(f'Sem{sem}-{typ}')
        context['type'] = type
        form = Form(request.POST)

        if request.POST.get('show',False):
            return render(request, "Student_app/result.html", context)

        if e_type:
            valid = form.is_valid() or (request.session.get('session-key') == request.POST.get('session-key') and request.POST.get('session-key') != None)
            request.session['session-key'] = generate_password()
            if not request.user.is_authenticated:
                enroll = form.cleaned_data.get('enrollment')
            else:enroll = request.user.username
            if not valid:
                messages.error(request,'Invalid captcha')
                context['form'] = Form(initial={'enrollment': enroll})
                return render(request, "Student_app/result.html", context)
            if not request.user.is_authenticated:
                try:
                    stu = app_stu.objects.get(stu_enroll=enroll)
                    stu_marks = Student_Marks.objects.filter(student=stu)
                    context['form'] = Form(initial={'enrollment':enroll})
                except app_stu.DoesNotExist:
                    messages.error(request,'Invalid enrollment number')
                    return render(request, "Student_app/result.html", context)




            sem = int(e_type[3])
            sttype = ses[0]+year+'-'+e_type.split('-')[1].title()
            marks = stu_marks.filter(stu_sem=sem, exam_type=sttype)
            if len(marks) < 1:
                messages.error(request,f'There is no Sem{sem}-{sttype} result for student Enrollment: {enroll}')
                return render(request, "Student_app/result.html", context)
            first = marks.first()
            context.update({
                'student_marks': marks,
                'first_mark': first,
                'student': first.student,
                'subject': first.subject,
                'sem': True,
                'pdf': True
            })
            if request.POST.get('pdf'):
                pdf = get_template("Student_app/pdf_result.html")
                pdf_render = pdf.render(context)
                custom_style = CSS(string='@page { size: A4; } body { transform: scale(1.1); }')
                # Generate PDF using WeasyPrint
                pdf_file = HTML(string=pdf_render).write_pdf(stylesheets=[custom_style])

                # Create an HTTP response with PDF content
                response = HttpResponse(pdf_file, content_type='application/pdf')
                response['Content-Disposition'] = f'{first.student.stu_name}filename="result.pdf"'
                return response
            request.session['session-key'] = s = generate_password()
            context['session_key'] = s
            context['enrollment'] = enroll
            return render(request,"Student_app/result.html",context)


        return render(request, 'Student_app/result.html', context)

    context['curr_session'] = session[0]
    ses,year = session[0].split('-')
    ty = published.filter(year=year,session=ses).values_list('sem','type').distinct().order_by('sem')
    type = []
    for sem,typ in ty:type.append(f'Sem{sem}-{typ}')
    context['type'] = type
    context['ctype'] = type[0]
    return render(request, 'Student_app/result.html', context)





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