from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student', 'certificate_title', 'course_name', 'issue_date', 'status')
    search_fields = ('certificate_id', 'student__full_name', 'student__register_number', 'certificate_title', 'course_name')
    list_filter = ('status', 'issue_date', 'issued_by')
    readonly_fields = ('certificate_id', 'created_at', 'updated_at')
