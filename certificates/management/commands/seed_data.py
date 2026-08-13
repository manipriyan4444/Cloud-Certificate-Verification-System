import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.utils import timezone
from datetime import timedelta

from accounts.models import Student
from certificates.models import Certificate
from certificates.utils import generate_certificate_id, create_qr_code_for_certificate

class Command(BaseCommand):
    help = 'Seeds 5 sample students and 5 sample certificates with QR codes for demo and testing.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding sample data..."))

        # Create Admin Superuser if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@certifycloud.edu',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user (username: 'admin', password: 'admin123')"))

        sample_students_data = [
            {
                'username': 'john_doe',
                'password': 'Student123!',
                'reg_no': 'REG-2026-001',
                'name': 'John Doe',
                'email': 'john.doe@student.edu',
                'department': 'Computer Science & Engineering',
                'year': '4th Year',
                'phone': '+1 555-0101',
            },
            {
                'username': 'jane_smith',
                'password': 'Student123!',
                'reg_no': 'REG-2026-002',
                'name': 'Jane Smith',
                'email': 'jane.smith@student.edu',
                'department': 'Information Technology',
                'year': '3rd Year',
                'phone': '+1 555-0102',
            },
            {
                'username': 'alex_jones',
                'password': 'Student123!',
                'reg_no': 'REG-2026-003',
                'name': 'Alex Jones',
                'email': 'alex.jones@student.edu',
                'department': 'Data Science',
                'year': '4th Year',
                'phone': '+1 555-0103',
            },
            {
                'username': 'emily_davis',
                'password': 'Student123!',
                'reg_no': 'REG-2026-004',
                'name': 'Emily Davis',
                'email': 'emily.davis@student.edu',
                'department': 'Cloud Computing & Cyber Security',
                'year': '2nd Year',
                'phone': '+1 555-0104',
            },
            {
                'username': 'michael_brown',
                'password': 'Student123!',
                'reg_no': 'REG-2026-005',
                'name': 'Michael Brown',
                'email': 'michael.brown@student.edu',
                'department': 'Software Engineering',
                'year': '4th Year',
                'phone': '+1 555-0105',
            },
        ]

        created_students = []
        for s_data in sample_students_data:
            user, u_created = User.objects.get_or_create(
                username=s_data['username'],
                defaults={
                    'email': s_data['email'],
                    'first_name': s_data['name'],
                }
            )
            if u_created:
                user.set_password(s_data['password'])
                user.save()

            student, st_created = Student.objects.get_or_create(
                register_number=s_data['reg_no'],
                defaults={
                    'user': user,
                    'full_name': s_data['name'],
                    'email': s_data['email'],
                    'department': s_data['department'],
                    'year': s_data['year'],
                    'phone_number': s_data['phone']
                }
            )
            created_students.append(student)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(created_students)} students."))

        sample_certs = [
            {
                'student': created_students[0],
                'title': 'Certified Cloud Architect & Engineer',
                'course': 'AWS Cloud Architecture & Microservices',
                'desc': 'Demonstrated mastery in cloud resource management, serverless setup, and AWS S3 storage integration.',
                'status': 'VALID',
                'issued_by': 'National Institute of Cloud Computing',
            },
            {
                'student': created_students[1],
                'title': 'Full-Stack Python & Django Developer',
                'course': 'Advanced Django Web Framework',
                'desc': 'Successfully built secure full-stack web applications with authentication, ORM, and REST APIs.',
                'status': 'VALID',
                'issued_by': 'Global Tech Academy',
            },
            {
                'student': created_students[2],
                'title': 'Cyber Security & Cryptography Specialist',
                'course': 'Network Security & Verification Systems',
                'desc': 'Excellence in digital signature verification and secure hashing implementations.',
                'status': 'VALID',
                'issued_by': 'Cyber Defense Alliance',
            },
            {
                'student': created_students[3],
                'title': 'Diploma in Data Analytics & Machine Learning',
                'course': 'Data Science & Predictive Modeling',
                'desc': 'Completed capstone project in automated statistical analysis and data visualization.',
                'status': 'REVOKED',
                'issued_by': 'Tech University',
            },
            {
                'student': created_students[4],
                'title': 'DevOps & CI/CD Pipeline Engineer',
                'course': 'Containerization & Cloud Deployment',
                'desc': 'Professional certification in Docker, PostgreSQL deployment, and cloud automation.',
                'status': 'VALID',
                'issued_by': 'Cloud Native Foundation',
            },
        ]

        dummy_pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"

        for cert_data in sample_certs:
            cert_id = generate_certificate_id()
            file_name = f"document_{cert_id}.pdf"
            
            cert = Certificate.objects.create(
                certificate_id=cert_id,
                student=cert_data['student'],
                certificate_title=cert_data['title'],
                course_name=cert_data['course'],
                description=cert_data['desc'],
                issue_date=timezone.now().date() - timedelta(days=30),
                status=cert_data['status'],
                issued_by=cert_data['issued_by']
            )
            cert.certificate_file.save(file_name, ContentFile(dummy_pdf_content), save=False)
            cert.save()

            # Generate QR Code
            create_qr_code_for_certificate(cert)
            cert.save()

            self.stdout.write(self.style.SUCCESS(f"Created Certificate {cert.certificate_id} for {cert.student.full_name} ({cert.status})"))

        self.stdout.write(self.style.SUCCESS("Sample data seeding complete! Admin login: admin / admin123, Student login: john_doe / Student123!"))
