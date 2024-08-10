# from faculty.models import *
import os

from django.db import models
from django.contrib import admin
from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from faculty.models import Faculty_Records
from django.dispatch import receiver
from datetime import datetime
from django.db.models.signals import post_save,pre_save
from user.models import Faculty
# Create your models here.

# Create your models here.
class Sub_Syllabus(models.Model):
    class Session(models.TextChoices):
        WINTER = 'WINTER' , 'Winter'
        SUMMER = 'SUMMER', 'Summer'
    sub_id = models.CharField(unique=True,primary_key=True,max_length=10,default='11-1111111')
    sub_name = models.CharField(max_length=100)
    sub_code = models.CharField(max_length=7)
    Assigned_Sub_Faculty = models.ForeignKey(Faculty_Records, on_delete=models.SET_NULL,null=True, default=11)
    session = models.CharField(max_length=50, choices=Session.choices, default=Session.SUMMER)
    sub_branch_code = models.CharField(max_length=2, default='16')
    sub_lacture_hours = models.IntegerField(default=0)
    sub_tutorial_hours = models.IntegerField(default=0)
    sub_practical_hours = models.IntegerField(default=0)
    sub_category = models.CharField(max_length=110,default='Program Core')
    sub_theory_mid1 = models.IntegerField(default=0)
    sub_theory_mid2 = models.IntegerField(default=0)
    sub_theory_micro = models.IntegerField(default=0)
    sub_theory_PA = models.IntegerField(default=0)
    sub_theory_ESE = models.IntegerField(default=0)
    sub_prctical_PA = models.IntegerField(default=0)
    sub_prctical_ESE = models.IntegerField(default=0)
    sub_sem = models.IntegerField(default=0)
    sub_credit = models.IntegerField(default=0)
    sub_academic_term = models.CharField(max_length=5)
    sub_pdf = models.FileField(upload_to='home/pdfs/syllabus')

    def total_marks(self):
        return self.sub_theory_PA+self.sub_theory_ESE+self.sub_prctical_PA+self.sub_prctical_ESE

    total_marks.short_description = 'Total Marks'

    def __str__(self):
        return self.sub_name


@receiver(pre_save, sender=Sub_Syllabus)
def add_PA(sender,instance,*args,**kwargs):
    instance.sub_theory_PA = (((instance.sub_theory_mid1 +  instance.sub_theory_mid2 ) //2) + instance.sub_theory_micro)
    instance.sub_id = f'{instance.sub_branch_code}-{instance.sub_code}'

class GtuExam(models.Model):
    class Type(models.TextChoices):
        REGULAR = 'REGULAR' , 'Regular'
        REMEDIAL = 'REMEDIAL', 'Remedial'
    id = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Sub_Syllabus,on_delete=models.SET_NULL,null=True)
    sub_code = models.CharField(max_length=7,default='0000000')
    sub_branch_code = models.CharField(max_length=2,default='16')
    sub_sem = models.IntegerField(default=0,verbose_name='Sem')
    sub_academic_term = models.CharField(max_length=5,verbose_name='Term')
    sub_session = models.CharField(max_length=6,verbose_name='Session')
    type = models.CharField(max_length=10, choices=Type.choices,default=Type.REGULAR)
    sub_pdf = models.FileField(upload_to='home/pdfs/exam')

    def delete(self, *args, **kwargs):
        # Delete the file first to avoid leaving orphaned files
        if self.sub_pdf:
            if os.path.isfile(self.sub_pdf.path):
                os.remove(self.sub_pdf.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.sub_code)





