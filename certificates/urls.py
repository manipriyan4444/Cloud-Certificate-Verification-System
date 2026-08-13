from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('my-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('my-certificates/', views.my_certificates, name='my_certificates'),

    # Student Management
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_create, name='student_create'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),

    # Certificate Management
    path('list/', views.certificate_list, name='certificate_list'),
    path('create/', views.certificate_create, name='certificate_create'),
    path('<int:pk>/', views.certificate_detail, name='certificate_detail'),
    path('<int:pk>/download/', views.certificate_download, name='certificate_download'),
    path('<int:pk>/revoke/', views.certificate_revoke, name='certificate_revoke'),
    path('<int:pk>/restore/', views.certificate_restore, name='certificate_restore'),
]
