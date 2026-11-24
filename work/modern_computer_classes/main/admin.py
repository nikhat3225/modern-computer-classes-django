from django.contrib import admin

from .models import (
    Course,
    Student,
    Enrollment,
    Payment,
    Certificate,
    Teacher,
    Assignment,
    ContactMessage,
    LiveClass
)

admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Enrollment)
admin.site.register(Payment)
admin.site.register(Certificate)
admin.site.register(Teacher)
admin.site.register(Assignment)
admin.site.register(ContactMessage)
admin.site.register(LiveClass)