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

        subjects = Sub_Syllabus.objects.filter(Assigned_Sub_Faculty=fac).order_by('-sub_sem')

        marks_work = ()
        row = {'semester': None, 'subject': tuple()}
        semester = subjects[0].sub_sem
        semester_remain = 0
        semester_total = 0
        Total = 0
        Remain = 0
        records = Student_Marks.objects.filter(Assigned_Sub_Faculty=fac)

        pass_work = ()
        pass_row = {'semester': None, 'subject': tuple()}
        pass_total = 0
        pass_remain = 0
        semester_pass_total = 0
        semester_pass_remain = 0

        for subject in subjects:
            if subject.sub_sem != semester:
                row['semester'] = {'sem': semester, 'sem_remain': semester_remain, 'sem_total': semester_total}
                marks_work += (row,)
                row = {'semester': None, 'subject': tuple()}

                pass_row['semester'] = {'sem': semester, 'sem_passed': semester_pass_remain,
                                        'sem_total': semester_pass_total}
                pass_work += (pass_row,)
                pass_row = {'semester': None, 'subject': tuple()}

                semester = subject.sub_sem
                Total += semester_total
                Remain += semester_remain
                pass_total += semester_pass_total
                pass_remain += semester_pass_remain

                semester_remain = 0
                semester_total = 0
                semester_pass_remain = 0
                semester_pass_total = 0




            sub = records.filter(subject=subject)
            total = len(sub)

            sub_pass = sub.filter(marks_entered=True)
            sub_passed = len(sub_pass.filter(is_passed=True))
            sub_total = len(sub_pass)

            remain = total - sub_total

            semester_remain += remain
            semester_total += total
            semester_pass_remain += sub_passed
            semester_pass_total += sub_total

            subject_marks_total = subject.total_marks()
            subject_marks_average = 0
            subject_marks_max = 0
            subject_marks_min = float('inf')
            if sub_total > 0:
                for record in sub_pass:
                    marks = record.total_marks()
                    subject_marks_average += marks
                    subject_marks_max = max(subject_marks_max, marks)
                    subject_marks_min = min(subject_marks_min, marks)

                subject_marks_average = float(float(subject_marks_average)/float(sub_total))
            row['subject'] += ({'sub_name': subject.sub_name, 'sub_remain': remain, 'sub_total': total},)
            pass_row['subject'] += ({'sub_name': subject.sub_name, 'sub_passed': sub_passed,
                                     'sub_total': sub_total,'sub_marks_total': subject_marks_total,
                                     'sub_marks_max': subject_marks_max,'sub_marks_min': subject_marks_min,
                                     'sub_marks_average':subject_marks_average},)

        row["semester"] = {'sem': semester, 'sem_remain': semester_remain, 'sem_total': semester_total}
        marks_work += (row,)
        Total += semester_total
        Remain += semester_remain

        pass_row["semester"] = {'sem': semester, 'sem_passed': semester_pass_remain,
                                        'sem_total': semester_pass_total}
        pass_work += (pass_row,)
        pass_total += semester_pass_total
        pass_remain += semester_pass_remain

        context.update({
            'title': self.title,
            'work': {'Total': {'total': Total, 'remain': Remain}, 'marks_work': marks_work},
            'pass_work': {'Total': {'total': pass_total, 'passed': pass_remain}, 'marks': pass_work},
            **(self.extra_context or {})
        })
        return context

    def get_coccntext_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fac = Faculty_Records.objects.get(user=self.request.user)

        subjects = Sub_Syllabus.objects.filter(Assigned_Sub_Faculty = fac).order_by('-sub_sem')

        marks_work = ()
        row = {'semester':None, 'subject':tuple()}
        semester = subjects[0].sub_sem
        semester_remain = 0
        semester_total = 0
        Total = 0
        Remain = 0
        records = Student_Marks.objects.filter(Assigned_Sub_Faculty = fac)
        for subject in subjects:
            if subject.sub_sem != semester:
                row['semester'] = {'sem':semester,'sem_remain': semester_remain,'sem_total': semester_total}
                marks_work += (row,)
                row = {'semester':None, 'subject':tuple()}
                semester = subject.sub_sem
                Total += semester_total
                Remain += semester_remain
                semester_remain = 0
                semester_total = 0
            sub = records.filter(subject = subject)
            remain = len(sub.filter(marks_entered=False))
            total = len(sub)
            semester_remain += remain
            semester_total += total
            row['subject'] += ({'sub_name':subject.sub_name,'sub_remain':remain,'sub_total':total},)
        row["semester"] = {'sem': semester, 'sem_remain': semester_remain,'sem_total': semester_total}
        marks_work += (row,)
        Total += semester_total
        Remain += semester_remain

        context.update({
            'title': self.title,
            'work':{'Total':{'total':Total,'remain':Remain},'marks_work':marks_work},
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
