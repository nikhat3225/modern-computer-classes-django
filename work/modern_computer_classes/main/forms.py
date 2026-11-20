from django import forms
from django.contrib.auth.models import User

from .models import (
    Student,
    Course,
    Assignment,
    Teacher,
    Certificate,
    Payment,
    Enrollment,
    ContactMessage,
    LiveClass,
)


class StudentForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Login username"
        }),
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Login password"
        }),
    )

    class Meta:
        model = Student
        fields = ["name", "email", "course", "status"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Student name"
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Email address"
            }),
            "status": forms.Select(choices=[
                ("Active", "Active"),
                ("Inactive", "Inactive"),
                ("Completed", "Completed"),
            ]),
        }

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Create username"
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Create password"
        })
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm password"
        })
    )

    class Meta:
        model = Student
        fields = ["name", "email", "course"]

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "Username already exists."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data["email"]

        if Student.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error(
                    "confirm_password",
                    "Passwords do not match."
                )

        return cleaned_data


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["name", "duration", "fees"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Course name"
            }),
            "duration": forms.TextInput(attrs={
                "placeholder": "e.g. 3 Months"
            }),
            "fees": forms.NumberInput(attrs={
                "placeholder": "e.g. 5000"
            }),
        }


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "course", "due_date"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "Assignment title"
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "Assignment details",
                "rows": 3,
                "style": "width:100%; padding:11px; border:1px solid #d5deea; border-radius:6px;",
            }),
            "due_date": forms.DateInput(attrs={
                "type": "date"
            }),
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["name", "email", "subject"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Teacher name"
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "Email address"
            }),
            "subject": forms.TextInput(attrs={
                "placeholder": "e.g. MS Office"
            }),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ["student", "course", "issue_date", "status"]
        widgets = {
            "issue_date": forms.DateInput(attrs={
                "type": "date"
            }),
            "status": forms.Select(choices=[
                ("Issued", "Issued"),
                ("Pending", "Pending"),
            ]),
        }


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ["student", "course", "status"]


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["student", "course", "amount", "status"]


class LiveClassForm(forms.ModelForm):
    class Meta:
        model = LiveClass
        fields = ["course", "teacher", "title", "start_time", "end_time", "meeting_link"]
        widgets = {
            "title": forms.TextInput(attrs={
                "placeholder": "e.g. Excel Formulas - Day 1"
            }),
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "meeting_link": forms.URLInput(attrs={
                "placeholder": "Zoom / Google Meet / YouTube Live link"
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and end_time <= start_time:
            self.add_error(
                "end_time",
                "End time must be after start time."
            )

        return cleaned_data


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "course", "message"]