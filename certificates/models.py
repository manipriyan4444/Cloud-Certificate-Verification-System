from django.db import models
from django.utils import timezone
from accounts.models import Student

class Certificate(models.Model):
    STATUS_CHOICES = [
        ('VALID', 'Valid'),
        ('REVOKED', 'Revoked'),
        ('EXPIRED', 'Expired'),
    ]

    certificate_id = models.CharField(max_length=50, unique=True, db_index=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    certificate_title = models.CharField(max_length=200)
    course_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    issue_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(blank=True, null=True)
    certificate_file = models.FileField(upload_to='certificates/docs/')
    qr_code = models.ImageField(upload_to='certificates/qrcodes/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='VALID')
    issued_by = models.CharField(max_length=150, default='Educational Institution')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.certificate_id} - {self.certificate_title} ({self.student.full_name})"

    @property
    def is_expired(self):
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return True
        return False

    def get_current_status(self):
        if self.status == 'REVOKED':
            return 'REVOKED'
        if self.is_expired:
            return 'EXPIRED'
        return 'VALID'
