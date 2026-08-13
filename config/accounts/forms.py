from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Student

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-custom',
        'placeholder': 'Enter Username or Register Number'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-custom',
        'placeholder': 'Enter Password'
    }))

class StudentForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'class': 'form-control form-control-custom',
        'placeholder': 'Username for login'
    }))
    password = forms.CharField(max_length=128, required=False, widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-custom',
        'placeholder': 'Leave blank to keep current password (when editing)'
    }))
    
    class Meta:
        model = Student
        fields = ['register_number', 'full_name', 'email', 'department', 'year', 'phone_number']
        widgets = {
            'register_number': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'e.g. REG2026001'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'student@example.com'}),
            'department': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'e.g. Computer Science'}),
            'year': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'e.g. 4th Year'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '+1234567890'}),
        }

    def clean_register_number(self):
        register_number = self.cleaned_data.get('register_number')
        student_id = self.instance.pk if self.instance else None
        if Student.objects.filter(register_number=register_number).exclude(pk=student_id).exists():
            raise forms.ValidationError("A student with this register number already exists.")
        return register_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        student_id = self.instance.pk if self.instance else None
        if Student.objects.filter(email=email).exclude(pk=student_id).exists():
            raise forms.ValidationError("A student with this email address already exists.")
        return email
