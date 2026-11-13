from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Sum
from django.views.decorators.http import require_POST

from .forms import StudentForm, CourseForm, AssignmentForm, TeacherForm, ContactForm
from .models import (
    Student, Course, Enrollment, Payment,
    Certificate, Teacher, Assignment, Contact,
)


# ------------- Public pages ----------

def home(request):
    return render(request, "index.html")


def courses(request):
    return render(request, "courses.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})


def gallery(request):
    return render(request, "gallery.html")


def registration(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        gender = request.POST.get("gender")
        course_id = request.POST.get("course")
        address = request.POST.get("address")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")

        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")

        elif not all([name, email, phone, username, password, gender, course_id]):
            messages.error(request, "Please fill all required fields!")

        elif gender not in ["Male", "Female", "Other"]:
            messages.error(request, "Please select a valid gender!")

        else:

            course = Course.objects.filter(id=course_id).first()

            if course is None:
                messages.error(request, "Please select a valid course!")

            else:

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                student = Student.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    gender=gender,
                    address=address,
                    user=user,
                    course=course
                )

                Enrollment.objects.create(
                    student=student,
                    course=course
                )

                messages.success(
                    request,
                    "Registration successful! Please login."
                )

                return redirect("login")

    courses = Course.objects.all()

    return render(request, "registration.html", {
        "courses": courses
    })

# ---------- Admin ----------

def is_admin(user):
    return user.is_authenticated and user.is_staff


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")

        messages.error(request, "Invalid admin username or password!")

    if request.GET.get("next"):
        messages.info(request, "Please login first to access the admin panel.")

    return render(request, "admin_login.html")


@user_passes_test(is_admin, login_url="admin_login")
def admin_dashboard(request):
    context = {
        "student_count": Student.objects.count(),
        "course_count": Course.objects.count(),
        "enrollment_count": Enrollment.objects.count(),
        "total_payments": Payment.objects.filter(status="Paid").aggregate(
            total=Sum("amount"))["total"] or 0,
        "students": Student.objects.select_related("course").order_by("-id"),
        "courses": Course.objects.all(),
        "enrollments": Enrollment.objects.select_related("student", "course"),
        "payments": Payment.objects.select_related("student", "course"),
        "certificates": Certificate.objects.select_related("student", "course"),
        "teachers": Teacher.objects.all(),
        "assignments": Assignment.objects.select_related("course").order_by("-id"),
        "student_form": StudentForm(),
        "course_form": CourseForm(),
        "assignment_form": AssignmentForm(),
        "teacher_form": TeacherForm(),
    }
    return render(request, "admin.html", context)


@require_POST
def admin_logout(request):
    logout(request)
    return redirect("home")


@user_passes_test(is_admin, login_url="admin_login")
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
                email=form.cleaned_data["email"],
            )
            student = form.save(commit=False)
            student.user = user
            student.save()
            messages.success(request, "Student added successfully with login account.")
        else:
            messages.error(request, "Please enter valid details. Username may already be taken.")
    return redirect("/admin_dashboard/#students")


@user_passes_test(is_admin, login_url="admin_login")
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Course added successfully.")
        else:
            messages.error(request, "Please enter valid course details.")
    return redirect("/admin_dashboard/#courses")


@user_passes_test(is_admin, login_url="admin_login")
def add_assignment(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment added successfully.")
        else:
            messages.error(request, "Please enter valid assignment details.")
    return redirect("/admin_dashboard/#assignments")


@user_passes_test(is_admin, login_url="admin_login")
def add_teacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher added successfully.")
        else:
            messages.error(request, "Please enter valid teacher details.")
    return redirect("/admin_dashboard/#teachers")


# ---------- Student ----------

def student_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and not user.is_staff:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid student username or password!")

    return render(request, "login.html")


@require_POST
def student_logout(request):
    logout(request)
    return redirect("home")


@login_required(login_url="login")
def student_dashboard(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(user=request.user).select_related("course").first()

    certificate_count = 0
    enrollment_count = 0
    assignments = []

    if student:
        certificate_count = Certificate.objects.filter(student=student).count()
        enrollment_count = Enrollment.objects.filter(student=student).count()
        if student.course:
            assignments = Assignment.objects.filter(
                course=student.course
            ).order_by("due_date")[:3]

    context = {
        "student": student,
        "certificate_count": certificate_count,
        "enrollment_count": enrollment_count,
        "assignments": assignments,
    }
    return render(request, "student_dashboard.html", context)


@login_required(login_url="login")
def my_courses(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(user=request.user).select_related("course").first()
    return render(request, "my_courses.html", {"student": student})


@login_required(login_url="login")
def my_certificates(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(user=request.user).first()

    certificates = []
    if student:
        certificates = Certificate.objects.filter(student=student).select_related("course")

    return render(request, "my_certificates.html", {
        "student": student,
        "certificates": certificates,
    })


@login_required(login_url="login")
def student_profile(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(user=request.user).select_related("course").first()
    return render(request, "student_profile.html", {"student": student})


@login_required(login_url="login")
def my_assignments(request):
    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(user=request.user).select_related("course").first()

    assignments = []
    if student and student.course:
        assignments = Assignment.objects.filter(course=student.course).order_by("due_date")

    return render(request, "my_assignments.html", {
        "student": student,
        "assignments": assignments,
    })

