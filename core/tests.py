from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import (
    Attendance,
    Books,
    Grades,
    MarkList,
    Parents,
    ReportCard,
    Semesters,
    Students,
    TeachersMessage,
)


class CoreModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="teacher", password="pass1234")
        self.book = Books.objects.create(name="Bible Stories", authors="MailBox")
        self.grade = Grades.objects.create(
            name="Nursery",
            grade_number=1,
            age_limit=5,
            book=self.book,
            academic_year=2018,
        )
        self.semester = Semesters.objects.create(name="First Semester")
        self.photo = SimpleUploadedFile(
            "student.jpg",
            b"fake-image-data",
            content_type="image/jpeg",
        )
        self.student = Students.objects.create(
            full_name="Samuel Doe",
            gender="M",
            age=6,
            school="Bright School",
            academic_grade=1,
            photo=self.photo,
            grades=self.grade,
            address="Addis Ababa",
        )
        self.parent = Parents.objects.create(
            full_name="Jane Doe",
            sex="F",
            phone_number="0911223344",
            role="Mother",
        )
        self.student.parents.add(self.parent)

    def test_student_grade_and_parent_relationships(self):
        self.assertEqual(self.student.grades.name, "Nursery")
        self.assertEqual(self.student.parents.count(), 1)
        self.assertEqual(self.grade.students.count(), 1)
        self.assertEqual(str(self.student), "Samuel Doe")

    def test_attendance_mark_and_report_card_creation(self):
        attendance = Attendance.objects.create(
            student=self.student,
            classes=self.grade,
            semester=self.semester,
            status="Present",
        )
        mark = MarkList.objects.create(
            classes=self.grade,
            student=self.student,
            semester=self.semester,
            out_of=20,
            category="Test",
            score=15,
        )
        report_card = ReportCard.objects.create(
            grade=self.grade,
            student=self.student,
            semester=self.semester,
        )

        self.assertEqual(str(attendance), f"{self.student.full_name} Present {attendance.date}")
        self.assertEqual(str(mark), f"{self.student}'s Mark List Test 15")
        self.assertEqual(report_card.grade, self.grade)
        self.assertEqual(report_card.student, self.student)

    def test_teacher_message_creation(self):
        message = TeachersMessage.objects.create(
            teacher=self.user,
            student=self.student,
            message="Please follow up with homework.",
        )

        self.assertEqual(message.student, self.student)
        self.assertIn("homework", message.message)


class CoreViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="pass1234", is_superuser=True, is_staff=True)
        self.book = Books.objects.create(name="Bible Stories", authors="MailBox")
        self.grade = Grades.objects.create(
            name="Nursery",
            grade_number=1,
            age_limit=5,
            book=self.book,
            academic_year=2018,
        )
        self.semester = Semesters.objects.create(name="First Semester")
        self.student = Students.objects.create(
            full_name="Martha Doe",
            gender="F",
            age=6,
            school="Bright School",
            academic_grade=2,
            photo=SimpleUploadedFile("student.jpg", b"fake-image-data", content_type="image/jpeg"),
            grades=self.grade,
            address="Addis Ababa",
        )
        self.parent = Parents.objects.create(
            full_name="Bob Doe",
            sex="M",
            phone_number="0999887766",
            role="Father",
        )
        self.student.parents.add(self.parent)

    def test_home_page_is_accessible(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Sunday School classes")

    def test_add_class_page_and_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:add_class"))
        self.assertEqual(response.status_code, 200)

        post_response = self.client.post(
            reverse("core:add_class"),
            {
                "name": "Primary One",
                "age_limit": 7,
                "grade_number": 2,
                "book": self.book.pk,
            },
        )

        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(Grades.objects.filter(name="Primary One").exists())

    def test_register_page_creates_student_and_parents(self):
        response = self.client.get(reverse("core:register"))
        self.assertEqual(response.status_code, 200)

        photo = SimpleUploadedFile("student.jpg", b"fake-image-data", content_type="image/jpeg")
        post_response = self.client.post(
            reverse("core:register"),
            {
                "student-full_name": "New Student",
                "student-gender": "M",
                "student-age": 5,
                "student-school": "New School",
                "student-academic_grade": 3,
                "student-address": "Somewhere",
                "parent1-full_name": "Parent One",
                "parent1-sex": "F",
                "parent1-phone_number": "0911111111",
                "parent1-role": "Mother",
                "parent2-full_name": "Parent Two",
                "parent2-sex": "M",
                "parent2-phone_number": "0922222222",
                "parent2-role": "Father",
                "photo_data": "",
                "student-photo": photo,
            },
        )

        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(Students.objects.filter(full_name="New Student").exists())
        self.assertEqual(Parents.objects.filter(full_name="Parent One").count(), 1)

    def test_student_detail_page_renders_and_accepts_message(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("core:student", args=[self.student.pk]))
        self.assertEqual(response.status_code, 200)

        post_response = self.client.post(
            reverse("core:student", args=[self.student.pk]),
            {"action": "save_message", "message": "Needs extra attention."},
        )

        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(TeachersMessage.objects.filter(message="Needs extra attention.").exists())

    def test_attendance_and_marklist_pages_work(self):
        response = self.client.get(reverse("core:attendance", args=[self.grade.pk]))
        self.assertEqual(response.status_code, 200)

        attend_response = self.client.post(
            reverse("core:attend"),
            {
                "student_id": [str(self.student.pk)],
                "status": ["Present"],
                "classes_id": [str(self.grade.pk)],
                "semester": "First Semester",
            },
        )
        self.assertEqual(attend_response.status_code, 200)
        self.assertTrue(Attendance.objects.filter(student=self.student).exists())

        mark_response = self.client.post(
            reverse("core:marklist", args=[self.grade.pk]),
            {
                "category": "Test",
                "out_of": 20,
                "semester": "First Semester",
                "student_id": [str(self.student.pk)],
                "mark": ["18"],
            },
        )
        self.assertEqual(mark_response.status_code, 200)
        self.assertTrue(MarkList.objects.filter(student=self.student).exists())

        print_response = self.client.get(reverse("core:print_attendance", args=[self.grade.pk]))
        self.assertEqual(print_response.status_code, 200)

        print_mark_response = self.client.get(reverse("core:print_marklist", args=[self.grade.pk]))
        self.assertEqual(print_mark_response.status_code, 200)

    def test_check_card_page_renders_report_cards(self):
        ReportCard.objects.create(
            grade=self.grade,
            student=self.student,
            semester=self.semester,
            test_and_assignments=80,
            attendance_class_activity_mark=70,
            exercise_book_mark=90,
            mid_final_mark=85,
            total=325,
            average_mark=81.25,
            rank=1,
        )
        response = self.client.get(reverse("core:check_card", args=[self.student.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Report cards")
