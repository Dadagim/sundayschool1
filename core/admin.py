from django.contrib import admin
from .models import *
# Register your models here.


admin.site.register(Semesters)
admin.site.register(Books)
admin.site.register(Parents)
admin.site.register(Students)
admin.site.register(Grades)
admin.site.register(TeachersMessage)
admin.site.register(Attendance)
admin.site.register(MarkList)
admin.site.register(ReportCard)

