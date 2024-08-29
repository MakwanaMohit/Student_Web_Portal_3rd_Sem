from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# from django.conf.urls.static import static
from .views import  *

urlpatterns = [
    path('',home,name='main home'),
    path('syllabus',syllabus,name='main syllabus'),
    path('exam',exam,name='main exam'),
]

# +static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
