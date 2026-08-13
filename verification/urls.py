from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('verify/', views.verify_public, name='verify_public'),
    path('verify/<str:certificate_id>/', views.verify_by_id, name='verify_by_id'),
    path('logs/', views.verification_logs, name='verification_logs'),
]
