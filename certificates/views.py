from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.utils import timezone

from .models import Certificate
from .forms import CertificateForm
from .utils import generate_certificate_id, create_qr_code_for_certificate
from accounts.models import Student
from accounts.forms import StudentForm
from verification.models import VerificationLog

def is_admin(user):
    return user.is_authenticated and user.is_staff

# ----------------- ADMIN DASHBOARD & MANAGEMENT ----------------- #

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_students = Student.objects.count()
    total_certificates = Certificate.objects.count()
    valid_certificates = Certificate.objects.filter(status='VALID').count()
    revoked_certificates = Certificate.objects.filter(status='REVOKED').count()
    expired_certificates = Certificate.objects.filter(expiry_date__lt=timezone.now().date()).exclude(status='REVOKED').count()
    total_verifications = VerificationLog.objects.count()

    recent_certificates = Certificate.objects.select_related('student').order_by('-created_at')[:5]
    recent_verifications = VerificationLog.objects.order_by('-verified_at')[:5]
    recent_students = Student.objects.order_by('-created_at')[:5]

    context = {
        'total_students': total_students,
        'total_certificates': total_certificates,
        'valid_certificates': valid_certificates,
        'revoked_certificates': revoked_certificates,
        'expired_certificates': expired_certificates,
        'total_verifications': total_verifications,
        'recent_certificates': recent_certificates,
        'recent_verifications': recent_verifications,
        'recent_students': recent_students,
    }
    return render(request, 'certificates/admin_dashboard.html', context)


# ----------------- STUDENT MANAGEMENT (ADMIN ONLY) ----------------- #

@login_required
@user_passes_test(is_admin)
def student_list(request):
    query = request.GET.get('q', '').strip()
    students_qs = Student.objects.all()

    if query:
        students_qs = students_qs.filter(
            Q(full_name__icontains=query) |
            Q(register_number__icontains=query) |
            Q(department__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(students_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'certificates/student_list.html', {
        'page_obj': page_obj,
        'query': query,
    })


@login_required
@user_passes_test(is_admin)
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password'] or 'Student@2026'
            
            if User.objects.filter(username=username).exists():
                messages.error(request, f"User with username '{username}' already exists.")
                return render(request, 'certificates/student_form.html', {'form': form, 'title': 'Add New Student'})

            user = User.objects.create_user(
                username=username,
                email=form.cleaned_data['email'],
                password=password,
                first_name=form.cleaned_data['full_name']
            )

            student = form.save(commit=False)
            student.user = user
            student.save()

            messages.success(request, f"Student '{student.full_name}' added successfully! Default login password: {password}")
            return redirect('student_list')
    else:
        form = StudentForm()

    return render(request, 'certificates/student_form.html', {'form': form, 'title': 'Add New Student'})


@login_required
@user_passes_test(is_admin)
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            password = form.cleaned_data.get('password')
            if password:
                student.user.set_password(password)
            student.user.email = student.email
            student.user.first_name = student.full_name
            student.user.save()

            messages.success(request, f"Student profile for '{student.full_name}' updated successfully.")
            return redirect('student_list')
    else:
        initial_data = {'username': student.user.username}
        form = StudentForm(instance=student, initial=initial_data)

    return render(request, 'certificates/student_form.html', {'form': form, 'student': student, 'title': 'Edit Student Profile'})


@login_required
@user_passes_test(is_admin)
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        user = student.user
        name = student.full_name
        student.delete()
        if user:
            user.delete()
        messages.success(request, f"Student '{name}' and associated user account deleted successfully.")
        return redirect('student_list')

    return render(request, 'certificates/student_confirm_delete.html', {'student': student})


@login_required
@user_passes_test(is_admin)
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    certificates = student.certificates.all()
    return render(request, 'certificates/student_detail.html', {
        'student': student,
        'certificates': certificates
    })


# ----------------- CERTIFICATE MANAGEMENT (ADMIN ONLY) ----------------- #

@login_required
@user_passes_test(is_admin)
def certificate_list(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    certificates_qs = Certificate.objects.select_related('student').all()

    if query:
        certificates_qs = certificates_qs.filter(
            Q(certificate_id__icontains=query) |
            Q(student__full_name__icontains=query) |
            Q(student__register_number__icontains=query) |
            Q(certificate_title__icontains=query) |
            Q(course_name__icontains=query)
        )

    if status_filter:
        certificates_qs = certificates_qs.filter(status=status_filter)

    paginator = Paginator(certificates_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'certificates/certificate_list.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
    })


@login_required
@user_passes_test(is_admin)
def certificate_create(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            
            # Auto-generate unique Certificate ID
            certificate.certificate_id = generate_certificate_id()
            certificate.save()

            # Generate QR Code pointing to verification URL
            create_qr_code_for_certificate(certificate, request=request)
            certificate.save()

            messages.success(request, f"Certificate created successfully! ID: {certificate.certificate_id}")
            return redirect('certificate_detail', pk=certificate.pk)
    else:
        form = CertificateForm()

    return render(request, 'certificates/certificate_form.html', {'form': form})


@login_required
def certificate_detail(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    
    # Permission check: Admin can view any, student can view only their own
    if not request.user.is_staff:
        if not hasattr(request.user, 'student_profile') or certificate.student != request.user.student_profile:
            return HttpResponseForbidden("You do not have permission to view this certificate.")

    logs = certificate.verification_logs.order_by('-verified_at')[:5]

    return render(request, 'certificates/certificate_detail.html', {
        'certificate': certificate,
        'logs': logs,
    })


@login_required
def certificate_download(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    
    if not request.user.is_staff:
        if not hasattr(request.user, 'student_profile') or certificate.student != request.user.student_profile:
            return HttpResponseForbidden("You do not have permission to download this certificate.")

    if not certificate.certificate_file:
        raise Http404("Certificate document file not found.")

    return FileResponse(certificate.certificate_file.open('rb'), as_attachment=True, filename=f"{certificate.certificate_id}_document")


@login_required
@user_passes_test(is_admin)
def certificate_revoke(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        certificate.status = 'REVOKED'
        certificate.save()
        messages.warning(request, f"Certificate {certificate.certificate_id} has been REVOKED.")
        return redirect('certificate_detail', pk=certificate.pk)

    return render(request, 'certificates/certificate_confirm_revoke.html', {'certificate': certificate})


@login_required
@user_passes_test(is_admin)
def certificate_restore(request, pk):
    certificate = get_object_or_404(Certificate, pk=pk)
    if request.method == 'POST':
        certificate.status = 'VALID'
        certificate.save()
        messages.success(request, f"Certificate {certificate.certificate_id} has been RESTORED to VALID status.")
        return redirect('certificate_detail', pk=certificate.pk)

    return render(request, 'certificates/certificate_confirm_restore.html', {'certificate': certificate})


# ----------------- STUDENT DASHBOARD & VIEWS ----------------- #

@login_required
def student_dashboard(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "No student profile associated with your user account.")
        return redirect('home')

    certificates = student.certificates.all()
    valid_count = certificates.filter(status='VALID').count()

    return render(request, 'certificates/student_dashboard.html', {
        'student': student,
        'certificates': certificates[:5],
        'total_certificates': certificates.count(),
        'valid_certificates': valid_count,
    })


@login_required
def my_certificates(request):
    if request.user.is_staff:
        return redirect('certificate_list')

    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "No student profile associated with your user account.")
        return redirect('home')

    certificates = student.certificates.all()

    return render(request, 'certificates/my_certificates.html', {
        'student': student,
        'certificates': certificates,
    })
