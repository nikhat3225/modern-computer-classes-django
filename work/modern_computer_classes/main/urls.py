
from django.urls import path
from . import views

urlpatterns = [

    # Public Pages
    path('', views.home, name='home'),
    path('registration/', views.registration, name='registration'),
    path('courses/', views.courses, name='courses'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('contact/', views.contact, name='contact'),

    # Tech Hub
    path('gallery/', views.tech_hub, name='gallery'),
    path('tech-hub/', views.tech_hub, name='tech_hub'),

    # Admin Pages
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_logout/', views.admin_logout, name='admin_logout'),

    # Admin Actions
    path('admin_dashboard/student/add/', views.add_student, name='add_student'),
    path('admin_dashboard/course/add/', views.add_course, name='add_course'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('admin_dashboard/assignment/add/', views.add_assignment, name='add_assignment'),
    path('admin_dashboard/teacher/add/', views.add_teacher, name='add_teacher'),
    path('admin_dashboard/certificate/add/', views.add_certificate, name='add_certificate'),
    path('admin_dashboard/enrollment/add/', views.add_enrollment, name='add_enrollment'),
    path('admin_dashboard/payment/add/', views.add_payment, name='add_payment'),

    # Student Login and Dashboard
    path('login/', views.student_login, name='login'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student_logout/', views.student_logout, name='student_logout'),

    # Student Pages
    path('my-courses/', views.my_courses, name='my_courses'),
    path('certificates/', views.my_certificates, name='my_certificates'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('assignments/', views.my_assignments, name='assignments'),
    path('my-assignments/', views.my_assignments, name='my_assignments'),
    path('student/live-classes/', views.student_live_classes, name='student_live_classes'),
    path('student/enrollments/', views.my_enrollments, name='my_enrollments'),

    # Enrollment
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('approve-enrollment/<int:enrollment_id>/', views.approve_enrollment, name='approve_enrollment'),
    path('reject-enrollment/<int:enrollment_id>/', views.reject_enrollment, name='reject_enrollment'),

    # Live Classes
    path('add-live-class/', views.add_live_class, name='add_live_class'),
    path('delete-live-class/<int:class_id>/', views.delete_live_class, name='delete_live_class'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('courses/ms-office/', views.ms_office, name='ms_office'),
    
]
