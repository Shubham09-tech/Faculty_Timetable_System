from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='timetable'),
    path('timetable/<str:entity_type>/<int:entity_id>/', views.select_semester, name='select_semester'),
    path('timetable/<str:entity_type>/<int:entity_id>/semester/<int:semester>/dashboard/', views.dashboard, name='dashboard'),
    path('timetable/<str:entity_type>/<int:entity_id>/semester/<int:semester>/dashboard/save_timetable/', views.save_timetable, name='save_timetable'),
    path('validation/',views.validation_home, name='validation'),
    path('validation/compare/',views.validation_compare, name='compare'),
    path('download/',views.download_home, name='download_home'),
    path('download/<int:branch_id>/<int:section_id>/<int:semester_id>/', views.timetable_download, name='timetable_download'),
    
]
   