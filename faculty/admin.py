from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Faculty_Records)
class Faculty_RecordsAdmin(admin.ModelAdmin):
    list_display = ('fac_name','email','user')
    def get_queryset(self, request):
        if not request.user.is_superuser:
            return Faculty_Records.objects.filter(email=request.user.email)
        return super().get_queryset(request)
    def get_readonly_fields(self, request, obj=None):
        li = ['user']+list(super().get_readonly_fields(request,obj))
        if not request.user.is_superuser:li.append('email')
        return li

    def has_change_permission(self, request, obj=None):
        if obj and 'nonedit@' in obj.email:
            return False
        return super().has_change_permission(request,obj)

    def has_delete_permission(self, request, obj=None):
        if obj and 'nonedit@' in obj.email:
            return False
        return super().has_delete_permission(request, obj)
