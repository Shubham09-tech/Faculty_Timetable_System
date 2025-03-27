from django.contrib import admin
from .models import Subject , Teacher ,Semester,Branch,Section,Class_Room,Timetable,Faculty

# Register your models here.

admin.site.register(Subject)
admin.site.register(Section)
admin.site.register(Branch)
admin.site.register(Semester)
admin.site.register(Teacher)
admin.site.register(Class_Room)
admin.site.register(Timetable)
admin.site.register(Faculty)
