from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from certificates.models import Certificate
from accounts.models import Student
from .models import VerificationLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def home_view(request):
    total_certificates = Certificate.objects.filter(status='VALID').count()
    total_verifications = VerificationLog.objects.count()
    
    return render(request, 'home.html', {
        'total_certificates': total_certificates,
        'total_verifications': total_verifications,
    })

def about_view(request):
    return render(request, 'about.html')

def verify_public(request):
    query_id = request.GET.get('certificate_id', '').strip() or request.POST.get('certificate_id', '').strip()
    if query_id:
        return redirect('verify_by_id', certificate_id=query_id)
    
    return render(request, 'verification/verify.html')

def verify_by_id(request, certificate_id):
    cert_id = certificate_id.strip().upper()
    client_ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

    try:
        certificate = Certificate.objects.select_related('student').get(certificate_id__iexact=cert_id)
        current_status = certificate.get_current_status()

        # Log verification attempt
        VerificationLog.objects.create(
            certificate=certificate,
            searched_certificate_id=cert_id,
            verification_status=current_status,
            ip_address=client_ip,
            user_agent=user_agent
        )

        return render(request, 'verification/result.html', {
            'status': current_status,
            'certificate': certificate,
            'searched_id': cert_id,
        })

    except Certificate.DoesNotExist:
        # Log failed verification attempt
        VerificationLog.objects.create(
            certificate=None,
            searched_certificate_id=cert_id,
            verification_status='NOT_FOUND',
            ip_address=client_ip,
            user_agent=user_agent
        )

        return render(request, 'verification/result.html', {
            'status': 'NOT_FOUND',
            'certificate': None,
            'searched_id': cert_id,
        })

@login_required
@user_passes_test(lambda u: u.is_staff)
def verification_logs(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    logs_qs = VerificationLog.objects.select_related('certificate').all()

    if query:
        logs_qs = logs_qs.filter(
            Q(searched_certificate_id__icontains=query) |
            Q(ip_address__icontains=query)
        )

    if status_filter:
        logs_qs = logs_qs.filter(verification_status=status_filter)

    paginator = Paginator(logs_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'verification/logs.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
    })
