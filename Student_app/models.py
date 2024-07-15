
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from datetime import datetime
from django.db.models.signals import post_save,pre_save
from django.db import models ,IntegrityError
from datetime import date
from user.models import *

from main.models import *
from faculty.models import Faculty_Records

# Create your models here.


class Student(models.Model):
    stu_name = models.CharField(max_length=50,default='')
    stu_enroll = models.CharField(max_length=12,unique=True,primary_key=True,default=000000000000,verbose_name= 'Student Enrollment Number')
    stu_sem = models.IntegerField()
    stu_DOB = models.DateField(default=date(2007,1,1))
    stu_branch = models.CharField(max_length=110)
    stu_branch_code = models.CharField(max_length=2,default='16')
    stu_mobile_num = models.CharField(max_length=10)
    stu_parents_mobile_num = models.CharField(max_length=10)
    stu_address = models.CharField(max_length=300)
    is_passed = models.BooleanField(default=True,verbose_name= 'Passed')
    is_passout = models.BooleanField(default=False,verbose_name='Passout')

    def __str__(self):
        return str(self.stu_enroll)



class Student_Marks(models.Model):
    class Session(models.TextChoices):
        WINTER = 'WINTER' , 'Winter'
        SUMMER = 'SUMMER', 'Summer'

    id = models.CharField(max_length=25,primary_key=True,unique=True,default='hello')
    student = models.ForeignKey('Student',on_delete=models.DO_NOTHING,default='0')
    stu_enroll = models.CharField(max_length=12,default='enrollmentno',verbose_name= 'Enrollment')
    stu_sem = models.IntegerField(default=5,verbose_name= 'Semester')
    stu_term = models.CharField(max_length=5,default='tern')
    stu_name = models.CharField(max_length=50,default='name')
    subject = models.ForeignKey(Sub_Syllabus,on_delete=models.DO_NOTHING)
    exam_type = models.CharField(max_length=14,default='S2023-Regular',verbose_name="Type")
    sub_name = models.CharField(max_length=50,default='thisissubjectname')
    Assigned_Sub_Faculty = models.ForeignKey(Faculty_Records,
                                             on_delete=models.SET_NULL,null=True, default=11,verbose_name='Faculty')
    stu_branch_code = models.CharField(max_length=2, default='16')
    stu_sub_code = models.IntegerField(default=0)
    session = models.CharField(max_length=50,
                               choices=Session.choices,default=Session.SUMMER)
    year = models.CharField(max_length=4,default='2022')
    stu_theory_ESE = models.IntegerField(default=0)
    stu_theory_PA = models.IntegerField(default=0)
    stu_practical_ESE = models.IntegerField(default=0)
    stu_practical_PA= models.IntegerField(default=0)
    marks_entered = models.BooleanField(default=False)
    is_passed = models.BooleanField(default=True, verbose_name='Passed')
    is_remedial = models.BooleanField(default=False)

    def total_marks(self):
        return self.stu_theory_PA + self.stu_theory_ESE + self.stu_practical_PA + self.stu_practical_ESE

    total_marks.short_description = 'Total Marks'

    def clean(self):
        if self.student.stu_branch_code != self.subject.sub_branch_code or self.student.stu_sem != self.subject.sub_sem:
            raise ValidationError({'subject': f"please select the subject that are available for this student"})
        if self.stu_theory_ESE<0 or self.stu_theory_ESE > self.subject.sub_theory_ESE:
            raise ValidationError({'stu_theory_ESE':f"therory ese marks cannot be greater then {self.subject.sub_theory_ESE} or less then 0"})
        pa = int((self.subject.sub_theory_mid1 + self.subject.sub_theory_mid2) / 2 + (self.subject.sub_theory_micro))
        if  self.stu_theory_PA<0 or self.stu_theory_PA > pa:
            raise ValidationError({'stu_theory_PA':f"therory pa marks cannot be greater then {pa} or less then 0"})
        if self.stu_practical_ESE<0 or self.stu_practical_ESE > self.subject.sub_prctical_ESE:
            raise ValidationError({'stu_practical_ESE':f"practical ese marks cannot be greater then {self.subject.sub_prctical_ESE} or less then 0"})
        if self.stu_practical_PA<0 or self.stu_practical_PA > self.subject.sub_prctical_PA:
            raise ValidationError({'stu_practical_PA':f"practical pa marks cannot be greater then {self.subject.sub_prctical_PA} or less then 0"})

    def __str__(self):
        return str(self.stu_enroll)
    #
    # def save(
    #     self, force_insert=False, force_update=False, using=None, update_fields=None
    # ):
    #     try:
    #         return super().save(force_insert=False, force_update=False, using=None, update_fields=None)
    #     except IntegrityError:
    #         raise ValidationError()

class upload_from_xlsx(models.Model):
    class name_model(models.TextChoices):
        STUDENT = 'STUDENT' , 'Student'
        STUDENTMARKS = 'STUDENTMARKS' , 'StudentMarks'
    upload_description = models.CharField(max_length=250,default=f'uploaded in')
    model_name = models.CharField(max_length=50,choices=name_model.choices)
    xlsx_file = models.FileField(upload_to='student/xlsx')

    def __str__(self):
        return self.upload_description


@receiver(pre_save, sender=upload_from_xlsx)
def add_name(sender,instance,*args,**kwargs):
    if 'uploaded in' in instance.upload_description:
        instance.upload_description = f'uploaded in {str(datetime.now())[:19]}'

@receiver(pre_save, sender=Student)
def add_prefix_to_id(sender, instance, *args, **kwargs):
    from .utils import branchlist

    instance.stu_branch = branchlist[instance.stu_branch_code]


@receiver(pre_save, sender=Student_Marks)
def add_prefix_to_id(sender, instance, *args, **kwargs):
    new_id= str(instance.session)[0]+str(instance.year)+str(instance.student.stu_enroll)+str(instance.subject.sub_code)
    if len(instance.id) <15:
        instance.id = new_id
        if instance.is_remedial:
            instance.exam_type = new_id[:5]+'-Remedial'
        else:
            instance.exam_type = new_id[:5]+'-Regular'
        instance.stu_sem = instance.subject.sub_sem
        instance.sub_name = instance.subject.sub_name
        instance.stu_term = instance.subject.sub_academic_term
        instance.stu_name = instance.student.stu_name
        instance.stu_enroll = instance.student.stu_enroll
        instance.stu_sub_code = instance.subject.sub_code
        instance.stu_branch_code = instance.student.stu_branch_code
        instance.Assigned_Sub_Faculty = instance.subject.Assigned_Sub_Faculty












