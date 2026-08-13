from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('register_number', 'full_name', 'email', 'department', 'year', 'created_at')
    search_fields = ('register_number', 'full_name', 'email', 'department')
    list_filter = ('department', 'year')
