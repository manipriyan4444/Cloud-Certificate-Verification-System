import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings

def generate_certificate_id():
    """
    Generates a unique Certificate ID in the format CERT-YYYY-XXXXX
    Example: CERT-2026-00001
    """
    from django.utils import timezone
    from certificates.models import Certificate
    
    current_year = timezone.now().year
    prefix = f"CERT-{current_year}-"
    
    latest_cert = Certificate.objects.filter(certificate_id__startswith=prefix).order_by('-certificate_id').first()
    
    if latest_cert:
        try:
            last_number = int(latest_cert.certificate_id.split('-')[-1])
            new_number = last_number + 1
        except ValueError:
            new_number = 1
    else:
        new_number = 1
        
    return f"{prefix}{new_number:05d}"


def create_qr_code_for_certificate(certificate, request=None):
    """
    Generates a QR code pointing to the real public verification URL for the certificate.
    """
    if request:
        base_url = request.build_absolute_uri('/')[:-1]
    else:
        base_url = "http://127.0.0.1:8000"
        
    verify_url = f"{base_url}/verify/{certificate.certificate_id}/"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="#0A192F", back_color="#FFFFFF")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    file_name = f"qr_{certificate.certificate_id}.png"
    
    certificate.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
