from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='allotment_home'),
    path('teacher-allocation/section/<int:section_id>/', views.teacher_allocation_by_section, name='teacher_allocation_by_section'),
    path('teacher-allocation/branch/<int:branch_id>/', views.teacher_allocation_by_branch, name='teacher_allocation_by_branch'),
    
]
