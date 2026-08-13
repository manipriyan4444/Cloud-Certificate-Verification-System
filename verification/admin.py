from django.contrib import admin
from .models import VerificationLog

@admin.register(VerificationLog)
class VerificationLogAdmin(admin.ModelAdmin):
    list_display = ('searched_certificate_id', 'verification_status', 'verified_at', 'ip_address')
    search_fields = ('searched_certificate_id', 'ip_address')
    list_filter = ('verification_status', 'verified_at')
    readonly_fields = ('certificate', 'searched_certificate_id', 'verified_at', 'verification_status', 'ip_address', 'user_agent')
