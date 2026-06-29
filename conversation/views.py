from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from core.models import Grades, Students

from .models import Programs
from .forms import ProgramForm, AnnouncementsForm
from .models import Announcements


# Create your views here.
def index(request):
    classes = Grades.objects.all()
    students = Students.objects.all()
    teachers = User.objects.all()

    my_classes = Grades.objects.filter(teachers__in=[request.user.id])
    return render(request, 'core/index.html', {'classes': classes, 'my_classes': my_classes,
                                               "students": students, 'teachers': teachers})



def program(request):
    programs = Programs.objects.all()
    form = ProgramForm()

    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("conversation:program")
    return render(request, 'conversation/program.html', {'programs': programs, 'form': form})


def announcements(request):
    announcements = Announcements.objects.all()
    form = AnnouncementsForm()

    if request.method == 'POST':
        form = AnnouncementsForm(request.POST, request.FILES)
        if form.is_valid():
            announce = form.save(commit=False)
            announce.sent_by = request.user
            announce.save()
            return redirect("conversation:announcements")




    return render(request, 'conversation/announcement.html', {'announcements': announcements, "form": form})