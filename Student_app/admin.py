from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.core.files.base import ContentFile
import io
from .models import *
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
import pandas as pd
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import render,redirect
from datetime import datetime


# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    model = Student
    fieldsets = (
        ("Student's personal details ", {
            'classes': ('collapse',),
            'fields': (('stu_name', 'stu_DOB'), ('stu_mobile_num', 'stu_parents_mobile_num'), 'stu_address'),
        }),
        ("Student's Academic Details  ", {
            'classes': ('collapse',),
            'fields': (('stu_enroll','stu_sem', ), ('stu_branch', 'stu_branch_code'),('is_passed', 'is_passout')),
        }),
    )
    # fields = ['stu_name','stu_enroll','stu_sem','stu_DOB','stu_branch','stu_branch_code','stu_mobile_num','stu_parents_mobile_num','stu_address','is_passed']
    list_display = ('stu_enroll','stu_name','stu_branch','stu_sem','is_passed','is_passout')
    list_filter = ('stu_sem','stu_branch')
    actions = ['next_term','make_marks_entry_for_Summer_Session','make_marks_entry_for_Winter_Session','generate_excel', 'upload_excel']

    def get_actions(self, request):
        actions = super().get_actions(request)

        if not request.user.is_superuser:
            if 'make_marks_entry_for_Summer_Session' in actions:
                del actions['make_marks_entry_for_Summer_Session']
            if 'make_marks_entry_for_Winter_Session' in actions:
                del actions['make_marks_entry_for_Winter_Session']
            if 'next_term' in actions:
                del actions['next_term']
        return actions
    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and ( request.POST['action'] == 'generate_excel' or  request.POST['action'] == 'make_marks_field'):
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in Student.objects.all():
                    stu = u.stu_enroll
                    if '1111' not in stu:
                        post.update({ACTION_CHECKBOX_NAME:str(stu)})
                        request._set_post(post)
        return super(StudentAdmin,self).changelist_view(request,extra_context)

    def next_term(self,request,queryset):
        pass
    def make_marks_entry_for_Winter_Session(self,request,queryset,):
        return self.make_marks_entry_for_Summer_Session(request,queryset,Sub_Syllabus.Session.WINTER)
    def make_marks_entry_for_Summer_Session(self,request,queryset,SESSION = Sub_Syllabus.Session.SUMMER):
        from main.models import Sub_Syllabus
        for student in queryset:
            if student.is_passed and not student.is_passout:
                stu_subjects = Sub_Syllabus.objects.filter(sub_sem=student.stu_sem,sub_branch_code=student.stu_branch_code)
                for subjects in stu_subjects:
                    try:
                        stu = Student_Marks.objects.create(
                        student=student,
                        subject=subjects,
                        session=SESSION,
                        year = datetime.now().year
                    )

                        stu.save()
                    except Exception as e:
                        print(e)
                        pass
                baclog = Student_Marks.objects.filter(student=student,is_passed=False)
                for bac in baclog:
                    subjects = bac.subject
                    try:
                        stu = Student_Marks.objects.create(
                        student=student,
                        subject=subjects,
                        session=SESSION,
                        is_remedial = True
                    )
                        stu.save()
                    except Exception as e:
                        print(e)
                        pass
    make_marks_entry_for_Summer_Session.short_description = "make new marks entry for Summer session of all subjects"
    make_marks_entry_for_Winter_Session.short_description = "make new marks entry for Winter session of all subjects"

    def delete_selected(self, request, queryset):
        # Exclude objects with roll number '1111'
        queryset = queryset.exclude(roll_number='1111')
        # Perform the default delete_selected action on the modified queryset
        return super().delete_selected(request, queryset=None)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:return True
        if obj and '1111' in obj.stu_enroll:
            return False
        super().has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        # if obj and '1111' in obj.stu_enroll:
        #     return [field.name for field in obj._meta.fields]
        return ['stu_branch','stu_enroll','stu_branch_code']

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion if the roll number is '1111'
        if obj and '1111' in obj.stu_enroll:
            return False
        return super().has_delete_permission(request, obj)

    def generate_excel(modeladmin, request, queryset):
        data = list(queryset.values())
        df = pd.DataFrame(data)
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        excel_buffer.seek(0)
        target_obj = upload_from_xlsx.objects.create(
            model_name=upload_from_xlsx.name_model.STUDENT
        )
        target_obj.xlsx_file.save(f'generated_excel.xlsx', ContentFile(excel_buffer.read()), save=True)

        modeladmin.message_user(request,'Now your xlsx record is created download xlsx file from this model edit and re upload in this then select create record action ')
        return redirect('/admin/Student_app/upload_from_xlsx/')


    generate_excel.short_description = "Generate Excel"

@admin.register(Student_Marks)
class Student_MarksAdmin(admin.ModelAdmin):
    model = Student_Marks
    fieldsets = (
        ('Enrollment number and other Info ', {
            'classes': ('collapse',),
            'fields': (('id','subject',
                       'Assigned_Sub_Faculty'), ('student','stu_branch_code', 'stu_sem')),
        }),
        ('Marks ,Session and Term ', {
            'classes': ('collapse',),
            'fields': (('session' ,'stu_term','is_passed','marks_entered'), ('stu_theory_ESE',
                                                 'stu_theory_PA', 'stu_practical_ESE', 'stu_practical_PA')),
         }),
        )
    # fields = ['id','student','subject','Assigned_Sub_Faculty','stu_sub_code','sub_name',
    #           'stu_branch_code','stu_name','stu_sem','session','stu_term','stu_theory_ESE',
    #           'stu_theory_PA', 'stu_practical_ESE','stu_practical_PA']
    list_display = ('stu_enroll','exam_type','marks_entered','is_passed', 'total_marks', 'subject', 'stu_name', 'Assigned_Sub_Faculty', 'stu_sem',)
    list_filter = ('marks_entered','sub_name','stu_branch_code','stu_sem','Assigned_Sub_Faculty','session','year')
    actions = ['generate_excel','process_xlsx']

    def changelist_view(self, request, extra_context=None):
        if 'action' in request.POST and request.POST['action'] == 'generate_excel':
            if not request.POST.getlist(ACTION_CHECKBOX_NAME):
                post = request.POST.copy()
                for u in self.get_queryset(request):
                    post.update({ACTION_CHECKBOX_NAME:str(u.id)})
                    request._set_post(post)
        return super(Student_MarksAdmin,self).changelist_view(request,extra_context)

    def get_queryset(self, request):
        # Get the current logged-in teacher
        if not request.user.is_superuser:
            current_teacher = Faculty_Records.objects.filter(user=request.user)
            if len(current_teacher) < 1:
                # messages.error(request, 'you are not a faculty to view this page ')
                return Student_Marks.objects.filter(id='S1111111111111111111')

            # Filter marks based on the assigned teacher
            queryset = super().get_queryset(request)
            return queryset.filter(Assigned_Sub_Faculty=current_teacher[0])
        return super().get_queryset(request)



    def has_delete_permission(self, request, obj=None):

        if obj and '11111111' in obj.id:
            return False
        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if obj and ('11111111' in obj.id):
            return False
        else: return super().has_change_permission(request,obj)

        # super().has_change_permission(request,obj)

    def get_readonly_fields(self, request, obj=None):
        base = ['id','stu_sem','stu_branch_code','sub_name','stu_term','stu_name','stu_enroll','stu_sub_code']
        if obj:
            return ['student','subject','session','Assigned_Sub_Faculty']+base
        if request.user.is_superuser:
            return base
        return base+['student','subject','session','Assigned_Sub_Faculty']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'student':
            kwargs['queryset'] = Student.objects.exclude(stu_enroll='111111111111')
        if db_field.name == 'subject':
            kwargs['queryset'] = Sub_Syllabus.objects.exclude(sub_code='1111111')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def generate_excel(modeladmin, request, queryset):

        for instance in queryset:
            if instance.is_remedial:
                instance.exam_type = instance.id[:5] + '-Remedial'
            else:
                instance.exam_type = instance.id[:5] + '-Regular'
            instance.save()
    #         marks = sum([record.stu_theory_ESE , record.stu_theory_PA , record.stu_practical_PA , record.stu_practical_ESE])
    #         if marks < 80:record.is_passed = False
    #         record.save()
    #

    #     data = list(queryset.values())
    #     df = pd.DataFrame(data)
    #     columns_to_exclude = ['student_id','subject_id','Assigned_Sub_Faculty_id','stu_branch_code']
    #     df = df.drop(columns=columns_to_exclude, errors='ignore')
    #
    #     excel_buffer = io.BytesIO()
    #     with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    #         df.to_excel(writer, index=False)
    #     excel_buffer.seek(0)
    #     target_obj = upload_from_xlsx.objects.create(
    #         model_name=upload_from_xlsx.name_model.STUDENTMARKS
    #         # Add other fields as needed...
    #     )
    #
    #     # Save the Excel file to the target model's FileField
    #     target_obj.xlsx_file.save(f'generated_excel.xlsx', ContentFile(excel_buffer.read()), save=True)
    #
    #     modeladmin.message_user(request,
    #                             'Now your xlsx record is created download xlsx file from this model edit and re upload in this then select create record action ')
    #     return redirect('/admin/Student_app/upload_from_xlsx/')
    #
    generate_excel.short_description = "Generate Excel"

@admin.register(upload_from_xlsx)
class upload_from_xlsxAdmin(admin.ModelAdmin):
    actions = ['process_xlsx']
    def get_readonly_fields(self, request, obj=None):
        return ['model_name']+list(super().get_readonly_fields(request,obj))

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        if not request.user.is_superuser:
            return upload_from_xlsx.objects.filter(model_name=upload_from_xlsx.name_model.STUDENTMARKS)
        query = super().get_queryset(request)

    def process_xlsx(modeladmin, request, queryset):
        for quir in queryset:
            xlsx_path = quir.xlsx_file.path
            df = pd.read_excel(xlsx_path)
            if quir.model_name == upload_from_xlsx.name_model.STUDENT and request.user.is_superuser:
                if request.user.is_superuser:
                    for index, row in df.iterrows():
                        try:
                            stu = Student.objects.create(
                            stu_name = row['stu_name'],
                            stu_enroll = row['stu_enroll'],
                            stu_sem = row['stu_sem'],
                            stu_DOB = row['stu_DOB'],
                            stu_branch = row['stu_branch'],
                            stu_branch_code = str(int(row['stu_branch_code'])),
                            stu_mobile_num = row['stu_mobile_num'],
                            stu_parents_mobile_num = row['stu_parents_mobile_num'],
                            stu_address = row['stu_address'])
                            stu.save()
                        except KeyError:
                            messages.error(request,'there is error with this excel file please check model name and use only excel file that generate from this site')
                            return redirect('/admin/Student_app/upload_from_xlsx/')
                        except Exception:
                            pass
            elif quir.model_name == upload_from_xlsx.name_model.STUDENTMARKS:
                for index, row in df.iterrows():
                    try:
                        stu = Student_Marks.objects.get(id=row['id'])
                        current_teacher = Faculty_Records.objects.filter(user=request.user)[0]
                        if stu.Assigned_Sub_Faculty == current_teacher:
                            stu.stu_theory_ESE = row['stu_theory_ESE']
                            stu.stu_theory_PA = row['stu_theory_PA']
                            stu.stu_practical_ESE = row['stu_practical_ESE']
                            stu.stu_practical_PA = row['stu_practical_PA']
                            stu.save()
                    except KeyError:
                        messages.error(request,
                                       'there is error with this excel file please check model name and use only excel file that generate from this site')
                        return redirect('/admin/Student_app/upload_from_xlsx/')
                    except ValidationError as val:
                        messages.error(request,
                                       str(val))
                        return redirect('/admin/Student_app/upload_from_xlsx/')


    process_xlsx.short_description = "Upload data from this file"