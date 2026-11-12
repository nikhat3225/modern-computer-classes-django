from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('registration/', views.registration, name='registration'),
    path('courses/', views.courses, name='courses'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery, name='gallery'),
    path("login/", views.student_login, name="login"),
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
path("student_logout/", views.student_logout, name="student_logout"),
path("my-courses/", views.my_courses, name="my_courses"),
path("certificates/", views.my_certificates, name="my_certificates"),
path("student-profile/", views.student_profile, name="student_profile"),
path("assignments/", views.my_assignments, name="my_assignments"),
path("admin_dashboard/course/add/", views.add_course, name="add_course"),
path("admin_dashboard/assignment/add/", views.add_assignment, name="add_assignment"),
path("admin_dashboard/teacher/add/", views.add_teacher, name="add_teacher"),
]