from django.urls import path
from .views import enter_score_parameters


urlpatterns = [
    path('bb/', enter_score_parameters, name='enter_score_parameters'),
]