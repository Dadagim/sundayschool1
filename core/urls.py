from django.urls import path

from . import views

app_name = 'core'


urlpatterns = [
    path("", views.home, name="home"),
    path("attend/", views.attend, name='attend'),
    path("register", views.Register_student, name="register"),
    path("grade/<int:grade_id>", views.details, name="detail"),
    path("student/<int:stud_id>", views.student_detail, name="student"),
    path("attendance/<int:pk>", views.attendance_view, name='attendance'),
#    path('attendance/pdf/', views.download_attendance_pdf, name='attendance_pdf'),
    path('add-class/', views.add_class, name='add_class'),
    path('ReportCard', views.prepareReportCard, name="report_card"),
    path('check-card/<int:student_pk>', views.check_card, name='check_card'),
    path("print-marklist/<int:class_pk>", views.print_marklist, name='print_marklist'),
    path("print-attendance/<int:class_pk>", views.print_attendance, name='print_attendance'),
    path("marklist/<class_pk>", views.marklist, name='marklist'),

]