from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from accounts.models import Student
from certificates.models import Certificate
from certificates.utils import generate_certificate_id, create_qr_code_for_certificate
from verification.models import VerificationLog

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser('admin_test', 'admin@test.com', 'AdminPass123!')
        self.student_user = User.objects.create_user('student_test', 'student@test.com', 'StudentPass123!')
        self.student_profile = Student.objects.create(
            user=self.student_user,
            register_number='REG-TEST-001',
            full_name='Test Student',
            email='student@test.com',
            department='Computer Science',
            year='4th Year'
        )

    def test_admin_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'AdminPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_student_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'student_test',
            'password': 'StudentPass123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'admin_test',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username/register number or password.")

    def test_unauthorized_admin_access(self):
        self.client.login(username='student_test', password='StudentPass123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302) # Redirects because not staff


class StudentManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('admin_mgr', 'admin@mgr.com', 'Pass123!')
        self.client.login(username='admin_mgr', password='Pass123!')

    def test_create_student(self):
        response = self.client.post(reverse('student_create'), {
            'username': 'new_student',
            'password': 'Pass123!Student',
            'register_number': 'REG-2026-999',
            'full_name': 'New Student',
            'email': 'newstudent@test.com',
            'department': 'Data Science',
            'year': '1st Year',
            'phone_number': '1234567890'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Student.objects.filter(register_number='REG-2026-999').exists())

    def test_duplicate_register_number(self):
        user = User.objects.create_user('st1', 'st1@test.com', 'pass')
        Student.objects.create(
            user=user, register_number='REG-DUP-001', full_name='St 1', email='st1@test.com',
            department='CS', year='1'
        )

        response = self.client.post(reverse('student_create'), {
            'username': 'st2',
            'register_number': 'REG-DUP-001',
            'full_name': 'St 2',
            'email': 'st2@test.com',
            'department': 'CS',
            'year': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A student with this register number already exists.")


class CertificateManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('admin_cert', 'admin@cert.com', 'Pass123!')
        self.client.login(username='admin_cert', password='Pass123!')
        
        self.student_user = User.objects.create_user('st_cert', 'stcert@test.com', 'Pass123!')
        self.student = Student.objects.create(
            user=self.student_user, register_number='REG-CERT-01', full_name='Cert Student',
            email='stcert@test.com', department='IT', year='3rd Year'
        )

    def test_certificate_id_generation(self):
        cert_id = generate_certificate_id()
        self.assertTrue(cert_id.startswith('CERT-'))

    def test_create_and_revoke_certificate(self):
        dummy_file = SimpleUploadedFile("cert.pdf", b"%PDF-1.4 dummy file content", content_type="application/pdf")
        
        response = self.client.post(reverse('certificate_create'), {
            'student': self.student.pk,
            'certificate_title': 'Cloud Engineering Certification',
            'course_name': 'AWS Solutions',
            'issue_date': '2026-08-13',
            'certificate_file': dummy_file,
            'issued_by': 'Cloud Academy'
        })
        self.assertEqual(response.status_code, 302)
        
        cert = Certificate.objects.get(student=self.student)
        self.assertEqual(cert.status, 'VALID')
        self.assertTrue(cert.qr_code)

        # Test Revocation
        revoke_response = self.client.post(reverse('certificate_revoke', kwargs={'pk': cert.pk}))
        self.assertEqual(revoke_response.status_code, 302)
        cert.refresh_from_db()
        self.assertEqual(cert.status, 'REVOKED')


class VerificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('vstudent', 'vstudent@test.com', 'pass')
        self.student = Student.objects.create(
            user=self.user, register_number='REG-V-01', full_name='Verification Student',
            email='vstudent@test.com', department='CS', year='2nd Year'
        )
        self.certificate = Certificate.objects.create(
            certificate_id='CERT-2026-00100',
            student=self.student,
            certificate_title='Mastery in Cybersecurity',
            course_name='Ethical Hacking',
            issue_date='2026-01-01',
            status='VALID'
        )

    def test_valid_public_verification(self):
        response = self.client.get(reverse('verify_by_id', kwargs={'certificate_id': 'CERT-2026-00100'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CERTIFICATE VERIFIED")
        self.assertContains(response, "Verification Student")
        
        # Verify Log entry created
        self.assertTrue(VerificationLog.objects.filter(searched_certificate_id='CERT-2026-00100', verification_status='VALID').exists())

    def test_revoked_public_verification(self):
        self.certificate.status = 'REVOKED'
        self.certificate.save()

        response = self.client.get(reverse('verify_by_id', kwargs={'certificate_id': 'CERT-2026-00100'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CERTIFICATE REVOKED")

    def test_not_found_verification(self):
        response = self.client.get(reverse('verify_by_id', kwargs={'certificate_id': 'CERT-INVALID-999'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CERTIFICATE NOT FOUND")
        self.assertTrue(VerificationLog.objects.filter(searched_certificate_id='CERT-INVALID-999', verification_status='NOT_FOUND').exists())
