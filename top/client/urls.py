from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('score/', enter_score_parameters, name='enter_score_parameters'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(),name="logout"),
    path('enter-score-parameters/', enter_score_parameters, name='enter_score_parameters'),
    path('view-score/', view_score, name='view_score'),
    path('view_tables/', view_tables, name='view_tables'),
    path('import/', import_data_from_excel, name='excel_file'),
    path('view_axes/', view_axes, name='view_axes'),
    path('view_all_score/', view_all_score, name='view_all_score'),
    path('client_scores/<int:client_id>/', client_scores, name='client_scores'),
    path('download-excel/', download_excel, name='download_excel'),
    path('generate_excel/', generate_excel, name='generate_excel'),
    path('axes_weight_list/', axes_weight_list, name='axes_weight_list'),
    path('statistics/', statistics, name='statistics'),



]