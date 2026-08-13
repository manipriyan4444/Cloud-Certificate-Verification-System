from django.db import models
from certificates.models import Certificate

class VerificationLog(models.Model):
    STATUS_CHOICES = [
        ('VALID', 'Valid'),
        ('REVOKED', 'Revoked'),
        ('EXPIRED', 'Expired'),
        ('NOT_FOUND', 'Not Found'),
    ]

    certificate = models.ForeignKey(Certificate, on_delete=models.SET_NULL, null=True, blank=True, related_name='verification_logs')
    searched_certificate_id = models.CharField(max_length=50)
    verified_at = models.DateTimeField(auto_now_add=True)
    verification_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-verified_at']

    def __str__(self):
        return f"[{self.verified_at.strftime('%Y-%m-%d %H:%M:%S')}] {self.searched_certificate_id} - {self.verification_status}"
