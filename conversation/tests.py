from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Announcements, Programs


class ConversationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="teacher2", password="pass1234")

    def test_program_and_announcement_creation(self):
        program = Programs.objects.create(
            date="2026-01-10",
            program_leader=self.user,
            memory_verse=self.user,
            song=self.user,
            bible_lesson=self.user,
            games=self.user,
        )
        announcement = Announcements.objects.create(
            message="Sunday school is rescheduled.",
            image=SimpleUploadedFile("image.jpg", b"fake-image-data", content_type="image/jpeg"),
            sent_by=self.user,
        )

        self.assertEqual(str(program), f"program for {program.date}")
        self.assertEqual(str(announcement), "announcement: Sunday school is rescheduled.")
        self.assertTrue(announcement.image)


class ConversationViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="teacher3", password="pass1234")

    def test_program_page_and_announcements_page_render(self):
        self.client.force_login(self.user)

        program_response = self.client.get(reverse("conversation:program"))
        self.assertEqual(program_response.status_code, 200)

        announcement_response = self.client.get(reverse("conversation:announcements"))
        self.assertEqual(announcement_response.status_code, 200)

    def test_program_form_and_announcement_form_post(self):
        self.client.force_login(self.user)

        program_response = self.client.post(
            reverse("conversation:program"),
            {
                "date": "2026-01-10",
                "program_leader": self.user.pk,
                "memory_verse": self.user.pk,
                "song": self.user.pk,
                "bible_lesson": self.user.pk,
                "games": self.user.pk,
            },
        )
        self.assertEqual(program_response.status_code, 302)
        self.assertTrue(Programs.objects.filter(program_leader=self.user).exists())

        announcement_response = self.client.post(
            reverse("conversation:announcements"),
            {
                "message": "New announcement",
            },
            follow=True,
        )
        self.assertEqual(announcement_response.status_code, 200)
        self.assertTrue(Announcements.objects.filter(message="New announcement").exists())
