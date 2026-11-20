from django.contrib import admin

from .models import Course, Student, Enrollment, Payment, Certificate, Teacher, Assignment, Contact

admin.site.register([Course, Student, Enrollment, Payment, Certificate, Teacher, Assignment, Contact])