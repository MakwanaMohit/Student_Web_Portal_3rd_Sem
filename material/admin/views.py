import datetime

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from main.models import Sub_Syllabus
from faculty.models import Faculty_Records
from Student_app.models import Student_Marks


class ThemesView(TemplateView):
    title = _('Theme selection')
    themes = (
        {'display': _('Default'), 'name': 'default'},
        {'display': _('Night'), 'name': 'night'},
        {'display': _('Black'), 'name': 'black'},
        {'display': _('Red'), 'name': 'red'},
        {'display': _('Green'), 'name': 'green'}
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'themes': self.themes,
            **(self.extra_context or {})
        })
        return context

    def post(self, request, *args, **kwargs):
        extra_kwargs = {}
        preview = request.POST.get('preview')
        save_action = request.POST.get('action')
        extra_kwargs['preview_theme'] = preview or save_action
        response = self.get(request, **extra_kwargs)
        if save_action:
            self.message_user(save_action)
            expires = datetime.datetime.now() + datetime.timedelta(days=365)
            response.set_cookie(key='current_theme', value=save_action, expires=expires)
        return response

    def message_user(self, theme_name):
        message = _('The "{}" theme was saved successfully.')
        messages.add_message(
            self.request, messages.SUCCESS,
            message.format(self._get_theme_display(theme_name)),
            fail_silently=True
        )

    def _get_theme_display(self, theme_name):
        themes = [theme['display'] for theme in self.themes if theme['name'] == theme_name]
        if themes:
            return themes[0]
        return _('Default')

class FacultyDashbordView(TemplateView):
    title = _('Dashbord')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fac = Faculty_Records.objects.get(user=self.request.user)

        subjects = Sub_Syllabus.objects.filter(Assigned_Sub_Faculty = fac).order_by('-sub_sem')

        dash_data = ()
        row = {'semester':None, 'subject':tuple()}
        semester = subjects[0].sub_sem
        semester_remain = 0
        records = Student_Marks.objects.filter(Assigned_Sub_Faculty = fac)
        for subject in subjects:
            if subject.sub_sem != semester:
                row['semester'] = {'sem':semester,'sem_remain': semester_remain}
                dash_data += (row,)
                row = {'semester':None, 'subject':tuple()}
                semester = subject.sub_sem
                semester_remain = 0
            remain = len(records.filter(subject = subject,marks_entered=False))
            semester_remain += remain
            row['subject'] += ({'sub_name':subject.sub_name,'sub_remain':remain},)
        row["semester"] = {'sem': semester, 'sem_remain': semester_remain}
        dash_data += (row,)
        for row in dash_data:
            print(row)
        context.update({
            'title': self.title,
            'dash_data':dash_data,
            **(self.extra_context or {})
        })
        return context
class AdminDashbordView(TemplateView):
    title = _('Dashbord')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            'dddname':'this is admin dashboard mohit is greate coder',
            **(self.extra_context or {})
        })
        return context
