from django import forms
from .models import Certificate
from accounts.models import Student
import os

ALLOWED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg']
MAX_FILE_SIZE_MB = 10

class CertificateForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select form-select-custom'}),
        empty_label="-- Select Student --"
    )

    class Meta:
        model = Certificate
        fields = [
            'student',
            'certificate_title',
            'course_name',
            'description',
            'issue_date',
            'expiry_date',
            'certificate_file',
            'issued_by'
        ]
        widgets = {
            'certificate_title': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'e.g. Master in Cloud Computing'}),
            'course_name': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'e.g. AWS & Django Development'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 3, 'placeholder': 'Brief details about the certificate'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control form-control-custom', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control form-control-custom', 'type': 'date'}),
            'certificate_file': forms.FileInput(attrs={'class': 'form-control form-control-custom', 'accept': '.pdf,.png,.jpg,.jpeg'}),
            'issued_by': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Issuing Institution / Organization'}),
        }

    def clean_certificate_file(self):
        file = self.cleaned_data.get('certificate_file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(f"Invalid file type. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}")
            if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise forms.ValidationError(f"File size exceeds the maximum allowed limit of {MAX_FILE_SIZE_MB}MB.")
        return file
