from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('score/', enter_score_parameters, name='enter_score_parameters'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(),name="logout"),
    

]