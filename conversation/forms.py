from django import forms

from .models import Programs

from .models import Announcements

STYLE  = "bg-black text-left text-white w-full border border-gray-300 p-3 rounded"

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Programs
        fields = '__all__'
        widgets = {
            'date': forms.DateTimeInput(attrs={'class':STYLE, 'type': 'date'}),
            "program_leader": forms.Select(attrs={'class':STYLE}),
            "song": forms.Select(attrs={'class':STYLE}),
            "memory_verse": forms.Select(attrs={'class':STYLE}),
            "bible_lesson": forms.Select(attrs={'class': STYLE}),
            "games": forms.Select(attrs={'class': STYLE}),

        }


class AnnouncementsForm(forms.ModelForm):
    class Meta:
        model = Announcements
        fields = ['message', "image"]
        widgets = {
            "message": forms.Textarea(attrs={"class": STYLE}),
            "image": forms.FileInput(attrs={"class": STYLE}),
        }