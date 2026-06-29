from django.db import models
from django.contrib.auth.models import  User


SEX = (
    ('M', 'Male'),
    ('F', 'Female'),
)
STATUS = (
    ("Present", 'Present'),
    ("Absent", 'Absent'),
    ("Permission", 'Permission'),
)
MARKCATEGORY_CHOICES = (
    ("Test",  "Test"),
    ("Exercise Book", "Exercise Book"),
    ("Class Activity", "Class Activity"),
    ("Mid Examination", "Mid Examination"),
    ("Final Examination", "Final Examination"),
    ("Assignment", "Assignment"),

)

SEMESTER_CHOICES = (
    ("First Semester", "First Semester"),
    ("Second Semester", "Second Semester"),
)



class Semesters(models.Model):
    name = models.CharField(max_length=100, choices=SEMESTER_CHOICES)


    def __str__(self):
        return self.name

class Books(models.Model):
    AUTHORS = (
        ("MailBox", 'MailBox'),
        ("OneHope", 'OneHope'),
    )
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='Books', null=True, blank=True)
    authors = models.CharField(choices=AUTHORS, max_length=100)

    def __str__(self):
        return f"{self.authors}'s {self.name}"

class Grades(models.Model):
    name = models.CharField(max_length=100)
    grade_number = models.PositiveIntegerField(null=True, blank=True)
    age_limit = models.PositiveIntegerField()
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name='grades')
    teacher = models.ManyToManyField(User, null=True, blank=True)
    isActive = models.BooleanField(default=True)
    academic_year = models.PositiveIntegerField()

    def __str__(self):
        return f'Grade {self.grade_number} - {self.name}'

class Parents(models.Model):

    ROLES = (
        ("Mother", 'Mother'),
        ("Father", 'Father'),
        ("Guardian", 'Guardian'),
    )

    full_name = models.CharField(max_length=100)
    sex = models.CharField(choices=SEX, max_length=100)
    phone_number = models.CharField(max_length=10)
    role = models.CharField(choices=ROLES, max_length=100)


    def __str__(self):
        return f'{self.full_name} {self.role}'

class Students(models.Model):
    full_name = models.CharField(max_length=100)
    gender  = models.CharField(choices=SEX, max_length=100)
    age = models.PositiveIntegerField()
    school = models.CharField(max_length=100)
    academic_grade = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='Students_photo')
    parents = models.ManyToManyField(Parents, related_name='students')
    grades = models.ForeignKey(Grades, on_delete=models.CASCADE, related_name='students', blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name}"

class TeachersMessage(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.teacher} {self.student}'

class Attendance(models.Model):

    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='attendance')
    classes = models.ForeignKey(Grades, on_delete=models.CASCADE, related_name='attendances', null=True)
    semester = models.ForeignKey(Semesters, on_delete=models.CASCADE, related_name='attendances', default="First Semester")
    status = models.CharField(max_length=30, choices=STATUS)
    date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ('student', 'classes', 'date')


    def student_status(student):
        row = []
        for a in Attendance.objects.filter(student=student):
            if a.student==student:
                row.append(a.status)

        return row

    def __str__(self):
        return f'{self.student.full_name} {self.status} {self.date}'


class MarkList(models.Model):
    classes = models.ForeignKey(Grades, on_delete=models.CASCADE, related_name='mark_list')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='marks')
    semester = models.ForeignKey(Semesters, on_delete=models.CASCADE, related_name='marks', default="First Semester")
    out_of = models.PositiveIntegerField()
    category = models.CharField(max_length=100, choices=MARKCATEGORY_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    score = models.PositiveIntegerField()


    def is_valid(self):
        if self.out_of < 0 or self.score < 0 or self.semester not in SEMESTER_CHOICES or self.category not in MARKCATEGORY_CHOICES:
            return False
        return True

    def __str__(self):
        return f"{self.student}'s Mark List {self.category} {self.score}"


class ReportCard(models.Model):
    grade = models.ForeignKey(Grades, on_delete=models.CASCADE, related_name='reports')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, related_name='report_cards')
    semester = models.ForeignKey(Semesters, on_delete=models.CASCADE, related_name='report_cards', blank=True, null=True)
    test_and_assignments = models.PositiveIntegerField(blank=True, null=True)
    attendance_class_activity_mark = models.PositiveIntegerField(blank=True, null=True)
    exercise_book_mark = models.PositiveIntegerField(blank=True, null=True)
    mid_final_mark = models.PositiveIntegerField(blank=True, null=True)
    total = models.PositiveIntegerField(blank=True, null=True)
    average_mark = models.FloatField(blank=True, null=True)
    rank = models.PositiveIntegerField(blank=True, null=True)


    class Meta:
        ordering = ["-average_mark"]
        unique_together = ('student', 'grade', 'semester')

    def is_valid_mark(self):
        if self.test_and_assignments > 100 or self.attendance_class_activity_mark > 100 or self.exercise_book_mark > 100 or self.mid_final_mark > 100:
            return False
        elif self.attendance_class_activity_mark < 0 or self.mid_final_mark < 0 or self.exercise_book_mark < 0 or self.test_and_assignments < 0:
            return False
        else:
            return True


    def calculate_attendance_class_activity_mark(self):
        try:
            attendance_dates = Attendance.objects.values_list('date', flat=True).distinct().order_by('date')
            attendance_taken = len(attendance_dates)

            marked = 50 / attendance_taken # attendance of one day will be out of
            present = Attendance.objects.filter(classes=self.grade, student=self.student, status='Present').count()
            permission = Attendance.objects.filter(classes=self.grade, student=self.student, status='Permisstion').count()

            class_activity = MarkList.objects.filter(classes=self.grade, student=self.student, category='Class Activity', semester=self.semester)

            class_activity_sum = 0
            class_activity_out_of = 0

            for mark in class_activity:
                class_activity_sum += mark.score
                class_activity_out_of += mark.out_of

            if class_activity_out_of > 50 or class_activity_out_of < 50:
                class_activity_sum = (class_activity_sum * 50) / class_activity_out_of

            total = int(marked * (present + permission)) + class_activity_sum

            if total > 100:
                raise ValueError("The class activity and attendance score don't match to total of 100")

            self.attendance_class_activity_mark = total
            return self.attendance_class_activity_mark
        except Exception as e:
            return e


    def test_assignment_mark(self):
        try:
            test = MarkList.objects.filter(classes=self.grade, student=self.student, category='Test')
            assignment = MarkList.objects.filter(classes=self.grade, student=self.student, category='Assignment')

            test_sum = 0
            test_count = 0
            test_out_of = 0

            for mark in test:
                test_count += 1
                test_out_of += mark.out_of
                test_sum += mark.score

            # if the sum of tests is not out of 50 change it to 50
            if test_out_of != 50:
                test_sum = (test_sum * 50) / test_out_of

            assignment_sum = 0
            assignment_count = 0
            assignment_out_of = 0

            for mark in assignment:
                assignment_count += 1
                assignment_out_of += mark.out_of
                assignment_sum += mark.score

            if assignment_out_of != 50:
                assignment_sum = (assignment_sum * 50) / test_out_of

            print(assignment_sum, test_sum)

            if test_sum + assignment_sum > 100:

                raise ValueError("Test assignment score don't match to total of 100.")

            self.test_assignment_mark = test_sum + assignment_sum
            return self.test_assignment_mark
        except Exception as e:
            return e


    def calc_mid_final_mark(self):
        try:
            mid_exam = MarkList.objects.get(classes=self.grade, student=self.student, category='Mid Exam', semester=self.semester)
            final_exam = MarkList.objects.get(classes=self.grade, student=self.student, category='Final Exam', semester=self.semester)


            if mid_exam.out_of != 40 and final_exam.out_of != 60:
                raise ValueError("The mid and Finals must be out of 40 and 60 respectively, please fix that problem.")



            self.mid_final_mark = mid_exam.score + final_exam.score
            return self.mid_final_mark
        except Exception as e:
            return e

    def calc_exercise_book_mark(self):
        try:
            mark = MarkList.objects.get(classes=self.grade, student=self.student, category='Exercise Book', semester=self.semester)

            exercise_book_mark = (mark.score * 100) / mark.out_of

            return exercise_book_mark
        except Exception as e:
            return e

    def total_mark(self, student):
        return (self.mid_final_mark + self.attendance_class_activity_mark + self.exercise_book_mark + self.test_and_assignments)

    def average(self, student):
        return (self.mid_final_mark + self.attendance_class_activity_mark + self.exercise_book_mark + self.test_and_assignments) / 4


    def calc_rank(self, student_):
        students = ReportCard.objects.filter(grade=student_.grades, semester=self.semester).order_by("-average_mark")

        print(students)
        hash_rank = {}
        start = 1

        for student in students:
            hash_rank[student.student.pk] = start
            start += 1

        self.rank = hash_rank[student_.pk]

        return self.rank




    def __str__(self):
        return f'{self.student.full_name} - {self.grade} - {self.rank}'























