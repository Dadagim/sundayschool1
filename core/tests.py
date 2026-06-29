from django.test import TestCase
from .models import *
from django.contrib.auth.models import User

# Create your tests here.


class TestReportCard(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(username="AAA", email="", password="1111")
        self.student = Students.objects.create(user=self.user)
