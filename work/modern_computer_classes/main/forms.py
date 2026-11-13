from django import forms
from django.contrib.auth.models import User
from .models import Student, Course, Assignment, Teacher, Certificate, Enrollment


class StudentForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Login username"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Login password"}),
    )

    class Meta:
        model = Student
        fields = ["name", "email", "course", "status"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Student name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address"}),
            "status": forms.Select(choices=[
                ("Active", "Active"),
                ("Inactive", "Inactive"),
                ("Completed", "Completed"),
            ]),
        }

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "duration", "fees"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Course name"}),
            "duration": forms.TextInput(attrs={"placeholder": "e.g. 3 Months"}),
            "fees": forms.NumberInput(attrs={"placeholder": "e.g. 5000"}),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "course", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Assignment title"}),
            "description": forms.Textarea(attrs={
                "placeholder": "Assignment details",
                "rows": 3,
                "style": "width:100%; padding:11px; border:1px solid #d5deea; border-radius:6px;",
            }),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["name", "email", "subject"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Teacher name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address"}),
            "subject": forms.TextInput(attrs={"placeholder": "e.g. MS Office"}),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ["student", "course", "issue_date", "status"]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "status": forms.Select(choices=[
                ("Issued", "Issued"),
                ("Pending", "Pending"),
            ]),
        }

        #enrollment form
        from .models import Enrollment

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course", "status"]