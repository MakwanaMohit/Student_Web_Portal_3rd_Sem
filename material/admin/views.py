import datetime
from django.shortcuts import HttpResponse
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
    title = _('Faculty Dashbord')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fac = Faculty_Records.objects.get(user=self.request.user)
        terms = list(Student_Marks.objects.filter(Assigned_Sub_Faculty = fac).values_list('stu_term',flat=True).distinct())
        terms.sort(key=lambda x:x[1:]+x[0],reverse=True)
        context.update({
            'title': self.title,
            'terms':terms,
            'fac':fac,
            **(self.extra_context or {})
        })
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        term = request.POST.get('term',context['terms'][0])
        context['term'] = term
        fac = context['fac']
        rec = get_faculty_subject_analytics(fac,term)
        if rec:context.update(rec)
        return self.render_to_response(context)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        term = context['terms'][0]
        context['term'] = term
        fac = context['fac']
        rec = get_faculty_subject_analytics(fac,term)
        if rec:context.update(rec)
        return self.render_to_response(context)


class AdminDashbordView(TemplateView):
    title = _('Admin Dashbord')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        terms = list(Student_Marks.objects.values_list('stu_term',flat=True).distinct())
        terms.sort(key=lambda x:x[1:]+x[0],reverse=True)
        context.update({
            'title': self.title,
            'terms':terms,
            **(self.extra_context or {})
        })
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        term = request.POST.get('term',context['terms'][0])
        context['term'] = term
        context['subject_analytics'] = get_admin_analytics(term)
        return self.render_to_response(context)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        term = context['terms'][0]
        context['term'] = term
        context['subject_analytics'] = get_admin_analytics(term)
        return self.render_to_response(context)

def get_faculty_subject_analytics(fac,term):
    records = Student_Marks.objects.filter(Assigned_Sub_Faculty=fac,stu_term=term).order_by('-stu_sem')
    subjects = Sub_Syllabus.objects.filter(sub_id__in=records.values_list('subject',flat=True).distinct())
    marks_work = ()
    row = {'semester': None, 'subject': tuple()}
    semester = subjects[0].sub_sem
    semester_remain = 0
    semester_total = 0
    Total = 0
    Remain = 0
    if len(records) < 1:return False
    Faculty = records[0].Assigned_Sub_Faculty
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
                                    'sem_total': semester_pass_total,'marks_entered':semester_pass_total>0}
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

        (total, remain, sub_total, sub_passed, subject_marks_total, subject_marks_average, subject_marks_max,
         subject_marks_min,marks_entered) = get_subject_analytics(subject,term)

        semester_remain += remain
        semester_total += total
        semester_pass_remain += sub_passed
        semester_pass_total += sub_total

        row['subject'] += ({'sub_name': subject.sub_name, 'sub_remain': remain, 'sub_total': total},)
        if marks_entered:
            pass_row['subject'] += ({'sub_name': subject.sub_name, 'sub_passed': sub_passed,
                                     'sub_total': sub_total, 'sub_marks_total': subject_marks_total,
                                     'sub_marks_max': subject_marks_max.total_marks(), 'sub_marks_min': subject_marks_min.total_marks(),
                                     'sub_max': subject_marks_max,'sub_min': subject_marks_min,
                                     'sub_marks_average': subject_marks_average,'marks_entered':True},)
        else:
            pass_row['subject'] += ({'sub_name': subject.sub_name, 'sub_passed': sub_passed,
                                     'sub_total': sub_total, 'sub_marks_total': subject_marks_total,
                                     'sub_marks_max': subject_marks_max, 'sub_marks_min': subject_marks_min,
                                     'sub_max': subject_marks_max,'sub_min': subject_marks_min,
                                     'sub_marks_average': subject_marks_average,'marks_entered':False},)

    row["semester"] = {'sem': semester, 'sem_remain': semester_remain, 'sem_total': semester_total}
    marks_work += (row,)
    Total += semester_total
    Remain += semester_remain

    pass_row["semester"] = {'sem': semester, 'sem_passed': semester_pass_remain,
                            'sem_total': semester_pass_total,'marks_entered':semester_pass_total>0}
    pass_work += (pass_row,)
    pass_total += semester_pass_total
    pass_remain += semester_pass_remain

    return {
        'Faculty':Faculty,
        'work': {'Total': {'total': Total, 'remain': Remain}, 'marks_work': marks_work},
        'pass_work': {'Total': {'total': pass_total, 'passed': pass_remain,'marks_entered':pass_total>0}, 'marks': pass_work},
    }


def get_admin_analytics(term):
    subjects = Student_Marks.objects.filter(stu_term=term).values_list('stu_sem', 'subject').distinct().order_by(
        'stu_sem')
    sem_subjects = []
    row = []
    last_sem = subjects[0][0]
    for sem, mark in subjects:
        if last_sem != sem:
            sem_subjects.append(row)
            row = []
            last_sem = sem
        if sem not in row:
            row.append(sem)
        row.append(mark)
    sem_subjects.append(row)

    Subject_analytics = []
    for sem in sem_subjects:
        subjects = sem[1:]
        subject_analytics = []
        sem_total = 0
        sem_remain = 0
        for subject in subjects:
            sub = Sub_Syllabus.objects.get(sub_id=subject)
            (total, remain, sub_total, sub_passed, subject_marks_total, subject_marks_average, subject_marks_max,
             subject_marks_min, marks_entered) = get_subject_analytics(sub, term)

            sem_total += total
            sem_remain += remain
            if marks_entered:
                subject_analytics.append({
                    'sub': sub, 'total': total, 'remain': remain, 'sub_total': sub_total, 'sub_passed': sub_passed,
                    'subject_marks_total': subject_marks_total, 'subject_marks_average': subject_marks_average,
                    'subject_marks_max': subject_marks_max.total_marks(),
                    'subject_marks_min': subject_marks_min.total_marks(),
                    'subject_max': subject_marks_max, 'subject_min': subject_marks_min, 'marks_entered': True
                })
            else:
                subject_analytics.append({
                    'sub': sub, 'total': total, 'remain': remain, 'sub_total': sub_total, 'sub_passed': sub_passed,
                    'subject_marks_total': subject_marks_total, 'subject_marks_average': subject_marks_average,
                    'subject_marks_max': subject_marks_max, 'subject_marks_min': subject_marks_min,
                    'subject_max': subject_marks_max, 'subject_min': subject_marks_min, 'marks_entered': False
                })
        Subject_analytics.append({
            'sem': sem[0], 'sem_total': sem_total, 'sem_remain': sem_remain,
            'subjects': subject_analytics
        })
    return Subject_analytics

def get_subject_analytics(subject,term):
    sub = Student_Marks.objects.filter(subject=subject,stu_term=term)
    sub_pass = sub.filter(marks_entered=True)

    sub_passed = sub_pass.filter(is_passed=True).count()
    total = sub.count()
    sub_total = sub_pass.count()
    remain = total - sub_total

    subject_marks_total = subject.total_marks()
    subject_marks_average = 0
    subject_marks_max = float('-inf')
    subject_max = None
    subject_marks_min = float('inf')
    subject_min = None
    if sub_total > 0:
        for record in sub_pass:
            marks = record.total_marks()
            subject_marks_average += marks
            if marks > subject_marks_max:
                subject_marks_max = marks
                subject_max = record
            if marks < subject_marks_min:
                subject_marks_min = marks
                subject_min = record

        subject_marks_average = float(float(subject_marks_average) / float(sub_total))


    return (total,remain,sub_total,sub_passed,subject_marks_total,subject_marks_average,subject_max,subject_min,sub_total > 0)
