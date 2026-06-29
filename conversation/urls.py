from django.urls import path
from .views import *

app_name = "conversation"

urlpatterns = [
    path('', index, name='index'),
    path("programs/", program, name='program'),
    path('announcements/', announcements, name='announcements'),
]
