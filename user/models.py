from django.db import models
from django.contrib.auth.models import AbstractUser , BaseUserManager

# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN' , 'Admin'
        STUDENT = 'STUDENT' , 'Student'
        FACULTY = 'FACULTY' , 'Faculty'
    base_role = Role.ADMIN
    role = models.CharField(max_length=50,choices=Role.choices)
    profile_picture = models.ImageField(upload_to='user/profile_pic/',blank=True,null=True)
    def save(self,*args,**kwargs):
        if not self.role:self.role = self.base_role
        if 'pbkdf2_sha' not in self.password:
            self.set_password(self.password)
        else: self.password = self.password
        return super().save(*args,**kwargs)


class StudentManager(BaseUserManager):
    def get_queryset(self,*args,**kwargs):
        result = super().get_queryset(*args,**kwargs)
        return result.filter(role=User.Role.STUDENT)

class Student(User):
    base_role = User.Role.STUDENT
    student = StudentManager()
    class Meta:
        proxy = True
class FacultyManager(BaseUserManager):
    def get_queryset(self,*args,**kwargs):
        result = super().get_queryset(*args,**kwargs)
        return result.filter(role=User.Role.FACULTY)

class Faculty(User):
    base_role = User.Role.FACULTY
    faculty = FacultyManager()
    class Meta:
        proxy = True