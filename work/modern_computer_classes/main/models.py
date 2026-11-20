
from django.db import models
from django.contrib.auth.models import User


# ================= COURSE =================

class Course(models.Model):
    name = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    fees = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name


# ================= STUDENT =================

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        default="Active"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ================= ENROLLMENT =================

class Enrollment(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    enrolled_on = models.DateField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"


# ================= PAYMENT =================

class Payment(models.Model):

    PAYMENT_CHOICES = [
        ("Cash", "Cash"),
        ("GPay", "Google Pay"),
        ("Card", "Debit / Credit Card"),
        ("UPI", "UPI"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default="Cash"
    )

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    def __str__(self):
        return f"{self.student.name} - ₹{self.amount}"


# ================= CERTIFICATE =================

class Certificate(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    issue_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        default="Pending"
    )

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"


# ================= TEACHER =================

class Teacher(models.Model):

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ================= LIVE CLASS =================

class LiveClass(models.Model):

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="live_classes"
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200)

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    meeting_link = models.URLField(
        help_text="Zoom / Google Meet / YouTube Live link"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.title} - {self.course.name}"


# ================= ASSIGNMENT =================

class Assignment(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE
    )

    due_date = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ================= CONTACT MESSAGE =================

class ContactMessage(models.Model):

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    course = models.CharField(max_length=100)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
