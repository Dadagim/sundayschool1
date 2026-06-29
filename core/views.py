from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from datetime import date, timedelta, timezone, datetime

from .forms import StudentForm, ParentForm, TeachersMessageForm, GradeForm
from .models import *
import base64
import uuid
from django.core.files.base import ContentFile

# Create your views here.
def home(request):
    grades = Grades.objects.filter(academic_year=datetime.now().year - 7, isActive=True)
    return render(request, "core/index.html", {"grades": grades})

# detail dashboard for a class
def details(request, grade_id):
    try:
        current_year = datetime.now().year
        grade = Grades.objects.get(pk=grade_id, academic_year=(int(current_year) - 7), isActive=True)

        cards = ReportCard.objects.filter(grade=grade).count()

        return render(request, "core/detail.html", {"grade": grade, "cards":cards})

    except ObjectDoesNotExist:
        messages.error(request, "Grade not found")
        return render(request, "core/404.html")


def student(request, stud_id):
    try:
        current_year = datetime.now().year
        student = Students.objects.get( pk=stud_id, academic_year=(current_year - 7), isActive=True)

        return render(request, "core/student.html", {"student": student})

    except ObjectDoesNotExist:
        messages.error(request, "Student not found")
        return render(request, "core/404.html")

def add_class(request):
    form = GradeForm()

    if request.method == 'POST':
        form = GradeForm(request.POST, request.FILES)
        if form.is_valid():
            grade = form.save(commit=False)
            current_year = datetime.now().year
            grade.academic_year = current_year - 7
            grade.save()
            return redirect('core:detail', grade_id=grade.pk)
        else:
            return render(request, 'core/add_class.html', {'form': form})
    else:
        return render(request, 'core/add_class.html', {'form': form})




# over all registration of sundayschool students
def Register_student(request):
    #from initializations
    student_form = StudentForm(prefix="student")
    parent1_form = ParentForm(request.POST, request.FILES, prefix="parent1")
    parent2_form = ParentForm(request.POST, request.FILES, prefix="parent2")

    if request.method == "POST":
        # get the information form the three forms
        student_form = StudentForm(request.POST, request.FILES, prefix="student")
        parent1_form = ParentForm(request.POST, request.FILES, prefix="parent1")
        parent2_form = ParentForm(request.POST, request.FILES, prefix="parent2")


        if student_form.is_valid() and parent1_form.is_valid() and parent2_form.is_valid() :
            # first save the parents then relate the parents to the student


            new_student = student_form.save(commit=False)

            # If a webcam capture was submitted as base64 data, decode and attach it
            photo_data = request.POST.get('photo_data')
            print(photo_data)
            if photo_data:
                # expected format: data:image/jpeg;base64,/9j/4AAQ...
                try:
                    header, data = photo_data.split(';base64,')
                    file_ext = 'jpg'
                    if 'png' in header:
                        file_ext = 'png'
                    file_name = f"student_{uuid.uuid4().hex[:10]}.{file_ext}"
                    decoded_file = base64.b64decode(data)
                    new_student.photo.save(file_name, ContentFile(decoded_file), save=False)
                except Exception:
                    pass

            #find if there is a parent registered before for brothers and sisters
            parent1_phone = parent1_form.cleaned_data['phone_number']
            parent2_phone = parent2_form.cleaned_data['phone_number']
            parent1_name = parent1_form.cleaned_data['full_name']
            parent2_name = parent2_form.cleaned_data['full_name']

            try:
                existing_parent1 = Parents.objects.get( phone_number=parent1_phone.strip(),
                                                     full_name=parent1_name.strip())
                existing_parent2 = Parents.objects.get(phone_number=parent2_phone.strip(),
                                                     full_name=parent2_name.strip())

                parent1 = existing_parent1
                parent2 = existing_parent2

                # add to the class that he belongs to
                grade = get_object_or_404(Grades, academic_year=2018, isActive=True, age_limit=int(new_student.age))

                if grade is None:
                    student.grade = None
                    messages.error(request, "Grade not found")
                    return redirect('/register')

                new_student.grades = grade

                # save the student

                new_student.save()
                new_student.parents.add(parent1)
                new_student.parents.add(parent2)

                messages.success(request, "Student successfully registered")
                return redirect('/register')
            except ObjectDoesNotExist:
                parent1_form.save()
                parent1_form.save()


            # add to the class that he belongs to
            grade = get_object_or_404(Grades, academic_year=2018, isActive=True, age_limit=int(new_student.age))

            if grade is None:
                student.grade = None
                messages.error(request, "Grade not found")
                return redirect('/register')

            new_student.grades = grade
            parent1 = parent1_form.save()
            parent2 = parent2_form.save()

            # save the student
            new_student.save()
            new_student.parents.add(parent1)
            new_student.parents.add(parent2)

            messages.success(request, "Student successfully registered")
            return redirect('/register')
        else:
            messages.error(request, "Invalid form")
            return redirect('/register')

    return render(request, "core/register.html", {"student_form": student_form,
                                                  "parent1_form": parent1_form,
                                                  "parent2_form": parent2_form})


def student_detail(request, stud_id):
    try:
        student = Students.objects.get(pk=stud_id)
        parents = student.parents.all()
        form = TeachersMessageForm()
        history = TeachersMessage.objects.filter(student=stud_id)

        if request.method == "POST":
            form = TeachersMessageForm(request.POST)

            if form.is_valid():
                message = form.save(commit=False)
                message.teacher = request.user
                message.student = student
                message.save()

                return redirect("core:student", stud_id)


        return render(request, "core/student_detail.html", {"student": student, "parents": parents, "form": form, "history": history})
    except ObjectDoesNotExist:
        messages.error(request, "Student not found")
        return render(request, "core/404.html")


def edit_student(request, stud_id):
    try:
        student = Students.objects.get(pk=stud_id)
        student_form = StudentForm(request.POST, request.FILES, instance=student)
        parents_form = ParentForm(request.POST, request.FILES)
        return render(request, "core/student_detail.html", {"student": student})
    except ObjectDoesNotExist:
        messages.error(request, "Student not found")
        return render(request, "core/404.html")



def attend(request):
    if request.method == 'POST':
        while True:
            try:
                students_id = request.POST.getlist('student_id')
                status = request.POST.getlist('status')
                classes = request.POST.getlist('classes_id')

                semester = request.POST.get('semester')
                print(classes)

                for student_id in range(len(students_id)):
                    student = Attendance.objects.create(student=get_object_or_404(Students,
                                                        pk=students_id[student_id]),
                                                        semester=get_object_or_404(Semesters, name=semester),
                                                        status=status[int(student_id)],
                                                        classes=get_object_or_404(Grades,
                                                        pk=classes[student_id]))

                attendance = Attendance.objects.filter(classes=classes[0])
                return render(request, "core/print_attendance.html", {'attendance': attendance})

            except ObjectDoesNotExist:
                messages.error(request, "NO such student")
                return render(request, "core/404.html")


def attendance_view(request, pk):
    try:
        students = Students.objects.filter(grades=pk).all()
        classes = Grades.objects.get(pk=pk)
        today = datetime.today().date()
        is_sunday = datetime.today().weekday() == 5

        taken_today = Attendance.objects.filter(classes=classes, date=today).count()

        if taken_today != 0:
            messages.success(request, "Attendance fro this week have already taken")
            return redirect("core:print_attendance", classes.pk)



        return render(request, 'core/attendance.html', {'students': students, "classes": classes, "is_sunday": is_sunday, "attendance_taken": taken_today})

    except ObjectDoesNotExist:
        messages.error(request, "This class doe not Exits")
        return render(request, "core/404.html")



def marklist(request, class_pk):
    try:
        students = Students.objects.filter(grades=class_pk)
        classes = get_object_or_404(Grades, pk=class_pk)
        if request.method == 'POST':
            assessment = request.POST.get("category")
            out_of = request.POST.get("out_of")
            semester  = request.POST.get("semester")


            students = request.POST.getlist("student_id")
            marks = request.POST.getlist('mark')


            for s in students:
                student = get_object_or_404(Students, pk=s)

            for student in range(len(students)):
                print(student)

                MarkList.objects.create(student=get_object_or_404(Students, pk=students[int(student)]),
                                        category=assessment,
                                        semester=Semesters.objects.get(name=semester),
                                        out_of=out_of,
                                        classes=get_object_or_404(Grades, pk=class_pk),
                                        score=marks[int(student)],
                                        )

            return HttpResponse("Done!")

        return render(request, "core/marklist.html", {
            "students": students,
            "classes": classes,

        })
    except Students.DoesNotExist as e:
        messages.error(request, e)
        return render(request, "core/404.html")


def print_attendance(request, class_pk):
    grade = Grades.objects.get(pk=class_pk)
    # 1. Get all unique dates where attendance was recorded, sorted chronologically
    attendance_dates = Attendance.objects.values_list('date', flat=True).distinct().order_by('date')

    # 2. Fetch students and optimize query with prefetch_related
    students = Students.objects.filter(grades=grade)

    # 3. Fetch all attendance records to build a lookup dictionary
    # Key format: (student_id, date) -> status
    attendance_records = Attendance.objects.filter(classes=grade)
    attendance_lookup = {
        (att.student_id, att.date): att.status
        for att in attendance_records
    }

    # 4. Build a structured list for the template
    matrix_data = []
    for student in students:
        student_row = {
            'id': student.id,
            'full_name': student.full_name,
            'statuses': []
        }
        # For every global date, check if this specific student has a record
        for date in attendance_dates:
            status = attendance_lookup.get((student.id, date), "-")  # Defaults to "-" if absent/no record
            if status == 'Present':
                student_row['statuses'].append("✅")
            elif status == 'Absent':
                student_row['statuses'].append("❌")
            elif status == "Permisstion":
                print(status)
                student_row['statuses'].append("📄")
            else:
                student_row['statuses'].append("⁉️")

        matrix_data.append(student_row)

    context = {
        'attendance_dates': attendance_dates,
        'matrix_data': matrix_data,
        "grade": grade,
    }
    return render(request, 'core/print_Attendance.html', context)


def print_marklist(request, class_pk):
    try:
        grade = Grades.objects.get(pk=class_pk)
        mark_list = MarkList.objects.filter(classes=grade)
        categories = set()
        students = set()
        marks = []
        single_mark = []
        for mark in mark_list:
            categories.add(mark.category)
            students.add(mark.student)
            student_mark = {
                "student": mark.student,
                "category": mark.category,

            }
            marks.append(student_mark)

        print(single_mark)




        return render(request, 'core/print_marklist.html', {
            'grade': grade,
            "categories": categories,
            "marks": marks,
        })




    except ObjectDoesNotExist:
        messages.error(request, "This class does not Exits")
        return render(request, "core/404.html")



def prepareReportCard(request):
    try:
        if request.method == 'POST':
            class_pk = int(request.POST.get("class_id"))
            semester_pk = int(request.POST.get("semester"))
            semester = Semesters.objects.get(pk=semester_pk)

            grade = get_object_or_404(Grades, pk=class_pk)

            students = Students.objects.filter(grades=grade)

            for student in students:
                card = ReportCard.objects.create(student=student, grade=grade, semester=semester)
                card.attendance_class_activity_mark = card.calculate_attendance_class_activity_mark()
                card.exercise_book_mark = card.calc_exercise_book_mark()
                card.test_and_assignments = card.calc_exercise_book_mark()
                card.mid_final_mark = card.calc_mid_final_mark()

                print(card.is_valid_mark())

                card.total = card.total_mark(student)
                card.average_mark = card.average(student)
                card.save()

            return HttpResponse("Done!")
    except Exception as e:
        return e


def check_card(request, student_pk):
    student = Students.objects.get(pk=student_pk)

    card = ReportCard.objects.get(student=student)
    card.rank = card.calc_rank(student)
    card.save()

    return render(request, 'core/check_card.html', {"student": student, "card": card})