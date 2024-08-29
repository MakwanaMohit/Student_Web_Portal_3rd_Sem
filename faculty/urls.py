from django.contrib import admin
from django.urls import path, include
from django.conf import settings
# from django.conf.urls.static import static
from .views import  *

urlpatterns = [
    path('/',home,name='faculty home'),
    path('/signup',signup,name='faculty signup'),
    path('/signin',signin,name='faculty signin'),
    path('/forgot',forgot,name='faculty forgot'),
    path('/signout',signout,name='faculty signout'),
]
# +static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
