"""
URL configuration for Student_Website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from captcha import urls
from faculty.views import dashbord
from django.conf.urls.static import static
from django.conf import settings
import os
urlpatterns = [
    # path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    # path('jet/', include('jet.urls', 'jet')),
    # path('grappelli/', include('grappelli.urls')),
    path('admin/', admin.site.urls,name='admin'),
    path('',include('main.urls')),
    path('captcha/',include('captcha.urls')),
    path('student',include('Student_app.urls')),
    path('faculty',include('faculty.urls'))
]

if os.environ.get('HOST_STATIC',False):
    urlpatterns += (static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT))

admin.site.site_header = 'Student Webstie Administration'
admin.site.index_title = 'Student Website'
admin.site.site_title = 'Student Website Administration'