from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django.db.models import Sum
from django.db import transaction
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import (
    ContactForm,
    RegistrationForm,
    StudentForm,
    CourseForm,
    AssignmentForm,
    TeacherForm,
    CertificateForm,
    EnrollmentForm,
    PaymentForm,
    LiveClassForm,
)

from .models import (
    Student,
    Course,
    Enrollment,
    Payment,
    Certificate,
    Teacher,
    Assignment,
    LiveClass,
)


# ---------- Helper ----------

def get_student_course_ids(student):

    course_ids = set()

    if student:
        course_ids.update(
            Enrollment.objects.filter(
                student=student,
                status="Active"
            ).values_list("course_id", flat=True)
        )

        if student.course_id:
            course_ids.add(student.course_id)

    return course_ids


# ---------- Public Home Page ----------

def home(request):
    return render(request, "index.html")


# ---------- Courses (Public) ----------

def courses(request):

    courses = Course.objects.all().order_by("name")

    return render(request, "courses.html", {
        "courses": courses
    })

def ms_office(request):
    return render(request, 'ms_office.html')

# ---------- Course Detail (Public) ----------

def course_detail(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    enrollment = None
    next_class = None

    if request.user.is_authenticated and not request.user.is_staff:

        student = Student.objects.filter(
            user=request.user
        ).first()

        if student:

            enrollment = Enrollment.objects.filter(
                student=student,
                course=course
            ).order_by("-id").first()

            if enrollment and enrollment.status == "Active":

                next_class = LiveClass.objects.filter(
                    course=course,
                    end_time__gte=timezone.now()
                ).select_related("teacher").first()

    return render(request, "course_detail.html", {
        "course": course,
        "enrollment": enrollment,
        "next_class": next_class,
    })


# ---------- Student Course Enrollment ----------

def enroll_course(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    if not request.user.is_authenticated:
        messages.warning(request, "Please login first to enroll in this course.")
        return redirect_to_login(request.get_full_path(), login_url="login")

    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(user=request.user).first()
    if not student:
        messages.error(request, "Student profile not found. Please contact admin.")
        return redirect("course_detail", course_id=course.id)

    enrollment = Enrollment.objects.filter(
        student=student, course=course
    ).order_by("-id").first()

    if enrollment and enrollment.status == "Active":
        messages.info(request, "You are already enrolled in this course.")
        return redirect("course_detail", course_id=course.id)

    # GET opens the paid form, even if an old Pending enrollment exists.
    if request.method == "GET":
        return render(request, "paid.html", {
            "course": course,
            "student": student,
        })

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "").strip()
        allowed_methods = {"Cash", "GPay", "Card", "UPI"}

        if payment_method not in allowed_methods:
            messages.error(request, "Please select a valid payment method.")
            return render(request, "paid.html", {
                "course": course, "student": student
            })

        existing_payment = Payment.objects.filter(
            student=student, course=course, status="Pending"
        ).first()

        if existing_payment:
            messages.info(
                request,
                "Your enrollment request is already submitted and is waiting for admin approval."
            )
            return redirect("student_dashboard")

        with transaction.atomic():
            if enrollment and enrollment.status == "Rejected":
                enrollment.status = "Pending"
                enrollment.save(update_fields=["status"])
            elif enrollment is None:
                enrollment = Enrollment.objects.create(
                    student=student, course=course, status="Pending"
                )

            Payment.objects.create(
                student=student,
                course=course,
                amount=course.fees,
                payment_method=payment_method,
                status="Pending"
            )

        messages.success(
            request,
            "Your enrollment request has been submitted successfully!"
        )
        return redirect("student_dashboard")

    return redirect("course_detail", course_id=course.id)


# ---------- Tech Hub ----------

@login_required(login_url="login")
def tech_hub(request):

    return render(request, "tech_hub.html")


# ---------- Student Registration ----------

def registration(request):

    if request.method == "POST":

        form = RegistrationForm(request.POST)

        if form.is_valid():

            try:

                with transaction.atomic():

                    user = User.objects.create_user(
                        username=form.cleaned_data["username"],
                        email=form.cleaned_data["email"],
                        password=form.cleaned_data["password"]
                    )

                    student = form.save(commit=False)
                    student.user = user
                    student.status = "Active"
                    student.save()

                messages.success(
                    request,
                    "Registration successful! Please login."
                )

                return redirect("login")

            except Exception as e:

                print("REGISTRATION ERROR:", e)

                messages.error(
                    request,
                    "Registration failed. Please try again."
                )

    else:

        form = RegistrationForm()

    return render(request, "registration.html", {
        "form": form
    })


# ---------- Admin Helper ----------

def is_admin(user):

    return user.is_authenticated and user.is_staff


# ---------- Admin Login ----------

def admin_login(request):

    if request.user.is_authenticated:

        if request.user.is_staff:
            return redirect("admin_dashboard")

        return redirect("student_dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login(request, user)

            return redirect("admin_dashboard")

        messages.error(
            request,
            "Invalid admin username or password!"
        )

    if request.GET.get("next"):

        messages.info(
            request,
            "Please login first to access the admin panel."
        )

    return render(request, "admin_login.html")


# ---------- Admin Dashboard ----------

@user_passes_test(is_admin, login_url="admin_login")
def admin_dashboard(request):

    context = {

        "student_count": Student.objects.count(),

        "course_count": Course.objects.count(),

        "enrollment_count": Enrollment.objects.count(),

        "total_payments": Payment.objects.filter(
            status="Paid"
        ).aggregate(total=Sum("amount"))["total"] or 0,

        "students": Student.objects.select_related(
            "course", "user"
        ).order_by("-id"),

        "courses": Course.objects.all(),

        "enrollments": Enrollment.objects.select_related(
            "student", "course"
        ).all().order_by("-id"),

        "payments": Payment.objects.select_related(
            "student", "course"
        ).all().order_by("-id"),

        "certificates": Certificate.objects.select_related(
            "student", "course"
        ),

        "teachers": Teacher.objects.all(),

        "assignments": Assignment.objects.select_related(
            "course"
        ).order_by("-id"),

        "live_classes": LiveClass.objects.select_related(
            "course", "teacher"
        ).order_by("-start_time"),

        "student_form": StudentForm(),

        "course_form": CourseForm(),

        "assignment_form": AssignmentForm(),

        "teacher_form": TeacherForm(),

        "certificate_form": CertificateForm(),

        "enrollment_form": EnrollmentForm(),

        "payment_form": PaymentForm(),

        "live_class_form": LiveClassForm(),
    }

    return render(request, "admin.html", context)


# ---------- Admin Logout ----------

@user_passes_test(is_admin, login_url="admin_login")
@require_POST
def admin_logout(request):

    logout(request)

    return redirect("admin_login")


# ---------- Add Student ----------

@user_passes_test(is_admin, login_url="admin_login")
def add_student(request):

    if request.method == "POST":

        form = StudentForm(request.POST)

        if form.is_valid():

            try:

                with transaction.atomic():

                    user = User.objects.create_user(
                        username=form.cleaned_data["username"],
                        password=form.cleaned_data["password"],
                        email=form.cleaned_data["email"],
                    )

                    student = form.save(commit=False)
                    student.user = user
                    student.save()

                messages.success(
                    request,
                    "Student added successfully with login account."
                )

            except Exception as e:

                print("ADD STUDENT ERROR:", e)

                messages.error(
                    request,
                    "Unable to add student. Username may already exist."
                )

        else:

            messages.error(
                request,
                "Please enter valid details. Username may already be taken."
            )

    return redirect("/admin_dashboard/#students")


# ---------- Add Course ----------

@user_passes_test(is_admin, login_url="admin_login")
def add_course(request):

    if request.method == "POST":

        form = CourseForm(request.POST, request.FILES)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Course added successfully."
            )

        else:

            messages.error(
                request,
                "Please enter valid course details."
            )

    return redirect("/admin_dashboard/#courses")


# ---------- Delete Course ----------

@require_POST
@user_passes_test(is_admin, login_url="admin_login")
def delete_course(request, course_id):

    course = get_object_or_404(Course, id=course_id)

    has_records = (
        Enrollment.objects.filter(course=course).exists()
        or Payment.objects.filter(course=course).exists()
        or Certificate.objects.filter(course=course).exists()
        or Assignment.objects.filter(course=course).exists()
        or LiveClass.objects.filter(course=course).exists()
    )

    if has_records:

        messages.error(
            request,
            "This course cannot be deleted because it has existing student or academic records."
        )

    else:

        course.delete()

        messages.success(
            request,
            "Course deleted successfully!"
        )

    return redirect("/admin_dashboard/#courses")


# ---------- Add Assignment ----------

@user_passes_test(is_admin, login_url="admin_login")
def add_assignment(request):

    if request.method == "POST":

        form = AssignmentForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Assignment added successfully."
            )

        else:

            messages.error(
                request,
                "Please enter valid assignment details."
            )

    return redirect("/admin_dashboard/#assignments")


# ---------- Add Teacher ----------

@user_passes_test(is_admin, login_url="admin_login")
def add_teacher(request):

    if request.method == "POST":

        form = TeacherForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Teacher added successfully."
            )

        else:

            messages.error(
                request,
                "Please enter valid teacher details."
            )

    return redirect("/admin_dashboard/#teachers")


# ---------- Generate Certificate ----------

@user_passes_test(is_admin, login_url="admin_login")
def add_certificate(request):

    if request.method == "POST":

        form = CertificateForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Certificate generated successfully!"
            )

        else:

            messages.error(
                request,
                "Please select valid student, course and certificate details."
            )

    return redirect("/admin_dashboard/#certificates")


# ---------- Enrollment Management ----------

@user_passes_test(is_admin, login_url="admin_login")
def add_enrollment(request):

    if request.method == "POST":

        form = EnrollmentForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Student enrolled successfully!"
            )

        else:

            messages.error(
                request,
                "Please select valid enrollment details."
            )

    return redirect("/admin_dashboard/#enrollments")


# ---------- Approve Enrollment ----------

@require_POST
@user_passes_test(is_admin, login_url="admin_login")
def approve_enrollment(request, enrollment_id):

    enrollment = get_object_or_404(
        Enrollment.objects.select_related("student", "course"),
        id=enrollment_id
    )

    enrollment.status = "Active"
    enrollment.save()

    student = enrollment.student

    if not student.course_id:

        student.course = enrollment.course
        student.save()

    messages.success(
        request,
        f"{student.name} ka enrollment approve ho gaya."
    )

    return redirect("/admin_dashboard/#enrollments")


# ---------- Reject Enrollment ----------

@require_POST
@user_passes_test(is_admin, login_url="admin_login")
def reject_enrollment(request, enrollment_id):

    enrollment = get_object_or_404(
        Enrollment.objects.select_related("student"),
        id=enrollment_id
    )

    enrollment.status = "Rejected"
    enrollment.save()

    messages.success(
        request,
        f"{enrollment.student.name} ka enrollment reject kar diya gaya."
    )

    return redirect("/admin_dashboard/#enrollments")


# ---------- Payment Management ----------

@user_passes_test(is_admin, login_url="admin_login")
def add_payment(request):

    if request.method == "POST":

        form = PaymentForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Payment added successfully!"
            )

        else:

            messages.error(
                request,
                "Please enter valid payment details."
            )

    return redirect("/admin_dashboard/#payments")


# ---------- Live Class Management ----------

@user_passes_test(is_admin, login_url="admin_login")
def add_live_class(request):

    if request.method == "POST":

        form = LiveClassForm(request.POST)

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Live class scheduled successfully!"
            )

        else:

            error_list = []

            for field_errors in form.errors.values():
                error_list.extend(field_errors)

            messages.error(
                request,
                "Please enter valid live class details. "
                + " ".join(error_list)
            )

    return redirect("/admin_dashboard/#liveclasses")


# ---------- Delete Live Class ----------

@require_POST
@user_passes_test(is_admin, login_url="admin_login")
def delete_live_class(request, class_id):

    live_class = get_object_or_404(
        LiveClass,
        id=class_id
    )

    live_class.delete()

    messages.success(
        request,
        "Live class deleted."
    )

    return redirect("/admin_dashboard/#liveclasses")


# ---------- Student Login ----------

def student_login(request):

    next_url = request.POST.get("next") or request.GET.get("next")

    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("admin_dashboard")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)
        return redirect("student_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and not user.is_staff:
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            return redirect("student_dashboard")

        messages.error(request, "Invalid student username or password!")

    return render(request, "login.html")


# ---------- Student Logout ----------

@login_required(login_url="login")
@require_POST
def student_logout(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    logout(request)

    return redirect("login")


# ---------- Student Dashboard ----------

@login_required(login_url="login")
def student_dashboard(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(
        user=request.user
    ).select_related("course").first()

    certificate_count = 0
    enrollment_count = 0
    assignments = []
    live_classes = []

    if student:

        certificate_count = Certificate.objects.filter(
            student=student
        ).count()

        enrollment_count = Enrollment.objects.filter(
            student=student,
            status="Active"
        ).count()

        course_ids = get_student_course_ids(student)

        if course_ids:

            assignments = Assignment.objects.filter(
                course_id__in=course_ids
            ).order_by("due_date")[:3]

        live_classes = LiveClass.objects.filter(
            course_id__in=course_ids,
            end_time__gte=timezone.now(),
        ).select_related("course", "teacher")[:3]

    context = {
        "student": student,
        "certificate_count": certificate_count,
        "enrollment_count": enrollment_count,
        "assignments": assignments,
        "live_classes": live_classes,
    }

    return render(
        request,
        "student_dashboard.html",
        context
    )


# ---------- My Courses ----------

@login_required(login_url="login")
def my_courses(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(
        user=request.user
    ).select_related("course").first()

    enrollments = Enrollment.objects.none()

    if student:

        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related("course").order_by("-enrolled_on")

    return render(request, "my_courses.html", {
        "student": student,
        "enrollments": enrollments,
    })


# ---------- My Enrollments ----------

@login_required(login_url="login")
def my_enrollments(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(
        user=request.user
    ).first()

    enrollments = []

    if student:

        enrollments = Enrollment.objects.filter(
            student=student
        ).select_related("course").order_by("-id")

    return render(request, "my_enrollments.html", {
        "student": student,
        "enrollments": enrollments,
    })


# ---------- Student Live Classes ----------

@login_required(login_url="login")
def student_live_classes(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(
        user=request.user
    ).select_related("course").first()

    course_ids = get_student_course_ids(student)

    now = timezone.now()

    classes = LiveClass.objects.filter(
        course_id__in=course_ids
    ).select_related("course", "teacher")

    return render(request, "student_live_classes.html", {
        "student": student,

        "live_now": classes.filter(
            start_time__lte=now,
            end_time__gte=now
        ),

        "upcoming": classes.filter(
            start_time__gt=now
        ),

        "past": classes.filter(
            end_time__lt=now
        ).order_by("-start_time")[:5],
    })


# ---------- My Certificates ----------

@login_required(login_url="login")
def my_certificates(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(
        user=request.user
    ).first()

    certificates = []

    if student:

        certificates = Certificate.objects.filter(
            student=student
        ).select_related("course")

    return render(request, "my_certificates.html", {
        "student": student,
        "certificates": certificates,
    })


# ---------- Student Profile ----------

@login_required(login_url="login")
def student_profile(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(
        user=request.user
    ).select_related("course").first()

    return render(request, "student_profile.html", {
        "student": student
    })


# ---------- My Assignments ----------

@login_required(login_url="login")
def my_assignments(request):

    if request.user.is_staff:
        return redirect("admin_dashboard")

    student = Student.objects.filter(
        user=request.user
    ).select_related("course").first()

    assignments = []

    if student:

        course_ids = get_student_course_ids(student)

        if course_ids:

            assignments = Assignment.objects.filter(
                course_id__in=course_ids
            ).order_by("due_date")

    return render(request, "my_assignments.html", {
        "student": student,
        "assignments": assignments,
    })


# ---------- Contact Form ----------

def contact(request):

    if request.method == "POST":

        form = ContactForm(request.POST)

        if form.is_valid():

            contact_data = form.save()

            subject = "New Contact Enquiry - Modern Computer Classes"

            message = f"""
New Contact Enquiry Received!

Name: {contact_data.name}
Phone: {contact_data.phone}
Email: {contact_data.email}
Course: {contact_data.course}

Message:
{contact_data.message}

Date: {contact_data.created_at}
"""

            recipients = [
                "nikhatshaikh3225@gmail.com",
                "mizbapathan2005@gmail.com",
            ]

            try:

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipients,
                    fail_silently=False,
                )

                messages.success(
                    request,
                    "Your message has been sent successfully!"
                )

            except Exception as e:

                print("EMAIL ERROR:", e)

                messages.warning(
                    request,
                    "Your message is saved, but email could not be sent."
                )

            return redirect("contact")

        else:

            messages.error(
                request,
                "Please check your details."
            )

    else:

        form = ContactForm()

    return render(request, "contact.html", {
        "form": form
    })