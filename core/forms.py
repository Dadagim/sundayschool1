from django import forms
from . import models
from .models import Grades

base_input_attrs = {
    "class": "block w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 shadow-sm outline-none transition focus:border-slate-400 focus:ring-4 focus:ring-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:focus:border-slate-600 dark:focus:ring-slate-900",
}

class StudentForm(forms.ModelForm):
    class Meta:
        model = models.Students
        fields = ["full_name", "gender", "age", "school", "academic_grade", "address"]
        widgets = {
            "full_name": forms.TextInput(attrs=base_input_attrs),
            "gender": forms.Select(attrs=base_input_attrs),
            "age": forms.NumberInput(attrs=base_input_attrs),
            "school": forms.TextInput(attrs=base_input_attrs),
            "academic_grade": forms.NumberInput(attrs=base_input_attrs),
            "address": forms.TextInput(attrs=base_input_attrs),
        }

# form for parents information
class ParentForm(forms.ModelForm):
    class Meta:
        model = models.Parents
        fields = '__all__'
        widgets = {
            "full_name": forms.TextInput(attrs=base_input_attrs),
            "sex": forms.Select(attrs=base_input_attrs),
            "phone_number": forms.TextInput(attrs=base_input_attrs),
            "role": forms.Select(attrs=base_input_attrs),
        }


class TeachersMessageForm(forms.ModelForm):
    class Meta:
        model = models.TeachersMessage
        fields = ("message",)
        widgets = {
            "message": forms.Textarea(attrs=base_input_attrs),
        }


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grades
        fields = ('name', 'age_limit', 'grade_number', 'book', 'teacher')
        widgets = {
            'name':forms.TextInput(attrs={'class':base_input_attrs}),
            'age_limit': forms.NumberInput(attrs={'class':base_input_attrs}),
            'grade':forms.NumberInput(attrs={'class':base_input_attrs}),
            'book': forms.Select(attrs={'class':base_input_attrs}),
            'teachers': forms.CheckboxSelectMultiple(),

        }
