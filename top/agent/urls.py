from django.urls import path
from .views import configure_score_parameters



urlpatterns = [
    path('aa/', configure_score_parameters, name='configure_score_parameters'),
]