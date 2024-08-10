# your_app/templatetags/form_filters.py
from django import template
from django.utils.html import format_html
register = template.Library()

@register.filter(name='add_class_to_div')
def add_class_to_div(form_as_div, css_class):
#     form_as_div = form_as_div.replace('<div class="' + css_class + '">', '')

#     # This will split the HTML by closing div tags and re-add the class
#     parts = form_as_div.split('</div>')
    return format_html('<h2>hello</h2>')
