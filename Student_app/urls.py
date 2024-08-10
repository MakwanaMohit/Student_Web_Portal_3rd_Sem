from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import  *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('' ,home,name="student home"),
    path('/',home),
    path('/signup',signup,name="student signup"),
    path('/signout',signout,name="student signout"),
    path('/result',result,name="student result"),
    path('/profile',profile,name="student profile"),
    path('/signin',signin,name="student signin"),
    path('/forgot',forgot,name="student forgot"),
    # path('signup/',signup,name="signout")
 ]
