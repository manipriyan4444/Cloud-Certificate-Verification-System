# COLLEGE PROJECT DOCUMENTATION

## PROJECT TITLE: Cloud-Based Certificate Verification and Management System Using QR Code
**Course / Subject**: Cloud Computing Mini Project  
**Tech Stack**: Python, Django, AWS S3, PostgreSQL, QR Code, HTML5, CSS3, Bootstrap 5

---

## 1. ABSTRACT
In recent years, the rampant proliferation of fraudulent academic certificates and fake credentials has undermined the credibility of educational institutions and recruiting organizations. Traditional physical certificates lack instant verification mechanisms, making manual background verification slow, cost-prohibitive, and vulnerable to forgery. 

This project presents a **Cloud-Based Certificate Verification and Management System Using QR Code**, a secure full-stack web application. The system enables educational institutions to issue tamper-evident certificates with auto-generated unique Certificate IDs (`CERT-YYYY-XXXXX`) and encrypted QR Codes. Uploaded documents and QR images are stored in **Amazon Web Services (AWS) S3 Cloud Object Storage**, while certificate metadata is maintained in a cloud-ready relational database (PostgreSQL/SQLite). Public users and recruiters can instantly verify any certificate by scanning its QR code or entering its Certificate ID without creating an account. Real-time audit logging captures every verification attempt for security monitoring.

---

## 2. INTRODUCTION
Educational certificates validate an individual’s academic accomplishments and professional qualifications. However, verifying paper or unencrypted digital PDF certificates requires contacting issuing institutions directly, creating delays in hiring workflows.

By leveraging **Cloud Computing** and **2D Barcode (QR Code) technology**, this application provides a centralized, scalable, and instant verification ecosystem. Built on Django's enterprise-grade framework, the platform combines cloud storage scalability with cryptographic access controls and audit capabilities.

---

## 3. PROBLEM STATEMENT
Educational institutions face significant challenges regarding credential integrity:
1. Physical paper certificates and standalone PDF files can easily be manipulated using photo-editing software.
2. Recruiters and third parties have no direct, real-time mechanism to validate certificate authenticity.
3. Traditional verification requires manual document dispatches or email inquiries, taking days or weeks.
4. On-premise storage servers suffer from hardware failures, limited bandwidth, and lack of cloud availability.

---

## 4. EXISTING SYSTEM & DISADVANTAGES

### Existing System
In the current manual system, certificates are printed on physical parchment or sent as static PDF attachments. Verification involves sending physical mail, phone inquiries, or third-party background check agencies.

### Disadvantages of Existing System
* **High Vulnerability to Forgery**: No digital signature or QR link embedded in the document.
* **Time-Consuming**: Verification takes anywhere from 5 to 15 business days.
* **High Administrative Costs**: Requires dedicated institutional staff to process verification letters manually.
* **Lack of Centralized Audit Log**: Institutions cannot track who verified which certificate or detect fraud attempts.
* **Storage Bottlenecks**: Local file servers lack cloud elasticity and high availability.

---

## 5. PROPOSED SYSTEM & OBJECTIVES

### Proposed System
The proposed **Cloud-Based Certificate Verification System** automates the entire lifecycle of certificate issuance, cloud storage, management, revocation, and public verification.

### Objectives
1. To develop a centralized cloud web application for institutional administrators and students.
2. To automate unique Certificate ID generation in `CERT-YYYY-XXXXX` format.
3. To dynamically generate QR codes linking directly to live server verification endpoints.
4. To integrate **AWS S3 Cloud Storage** for reliable, scalable media and document hosting.
5. To enable instant public verification (VALID / REVOKED / EXPIRED / NOT_FOUND) without login requirements.
6. To maintain audit records in `VerificationLog` for analytics and security tracking.

---

## 6. SCOPE & FEATURES

### Scope
The platform serves educational universities, certification bodies, corporate training institutes, students, and job recruiters globally over the internet.

### Features
* **Admin Dashboard**: Real-time stats (Total Students, Issued Certs, Valid, Revoked, Expired, Verifications).
* **Student Registry**: Complete student profile management with linked login credentials.
* **Certificate CRUD**: Issue certificates with PDF/Image uploads, auto-ID generation, and S3 upload.
* **Revocation & Restoration**: Administrative controls to revoke compromised certificates or restore valid status.
* **Public QR Verification**: Scan QR code or enter ID to view non-sensitive verified metadata.
* **Audit Trail**: Detailed verification logs capturing IP, timestamp, and User Agent.

---

## 7. MODULES DESCRIPTION

1. **Authentication & User Management Module (`accounts`)**:
   Handles Django authentication, hashed passwords, staff vs. student permission checks, profile views, and student registration.
2. **Certificate Management & QR Module (`certificates`)**:
   Manages certificate database records, file validation (type & size), auto-generation of unique IDs, QR code creation via Python `qrcode`, and document download stream.
3. **Public Verification & Audit Module (`verification`)**:
   Provides public verification views (`/verify/<certificate_id>/`), computes real-time validity status, hides sensitive student data, and records `VerificationLog` entries.
4. **Cloud Integration Layer**:
   Configures `boto3` and `django-storages` to push documents and QR images directly to AWS S3.

---

## 8. SYSTEM REQUIREMENTS

### Functional Requirements
* Admin must be able to log in securely and access administrative tools.
* System must generate unique non-repeating IDs (`CERT-2026-00001`).
* System must validate file extension (.pdf, .png, .jpg, .jpeg) and size (<= 10MB).
* System must generate a valid QR code pointing to the live URL.
* Public user must be able to view verification result without logging in.
* System must record client IP address and timestamp on every verification attempt.

### Non-Functional Requirements
* **Security**: Password hashing (PBKDF2), CSRF protection, SQL injection prevention via ORM, protection of private student data.
* **Performance**: Verification page load time < 1 second.
* **Availability**: 99.9% uptime powered by AWS Cloud Storage.
* **Usability**: Clean Dark Navy + Gold responsive user interface.

### Hardware & Software Requirements
* **OS**: Windows 10/11, Linux, or macOS
* **Python Version**: Python 3.10+ (Tested on 3.13)
* **Framework**: Django 5.2
* **Database**: SQLite for development, PostgreSQL for production
* **Cloud Storage**: AWS S3 Bucket
* **Browser**: Chrome, Firefox, Edge, Safari

---

## 9. ARCHITECTURE & DATABASE DESIGN

### Architecture Diagram Overview
```text
[ Client / Recruiter / Student ]
               │
               ▼ (HTTP/HTTPS)
    [ Django Web Server ]
      ├── URL Router & Views
      ├── Authentication & Security
      └── ORM Model Layer
               │
      ┌────────┴────────┐
      ▼                 ▼
[ AWS S3 Storage ]  [ Cloud Database ]
(Certs & QR Images)  (PostgreSQL / SQLite)
```

### ER Diagram Description
1. **User (Django Built-in)**: Stores authentication credentials.
2. **Student**: 1-to-1 relationship with User. Stores `register_number`, `full_name`, `email`, `department`, `year`, `phone_number`.
3. **Certificate**: ForeignKey to `Student`. Stores `certificate_id`, `certificate_title`, `course_name`, `issue_date`, `expiry_date`, `certificate_file` (S3 path), `qr_code` (S3 path), `status`, `issued_by`.
4. **VerificationLog**: ForeignKey to `Certificate`. Stores `searched_certificate_id`, `verified_at`, `verification_status`, `ip_address`, `user_agent`.

---

## 10. TESTING & RESULTS

### Unit Test Execution
Automated unit tests were created in `tests/test_all.py` covering 11 critical test cases:
* `test_admin_login` — PASS
* `test_student_login` — PASS
* `test_invalid_login` — PASS
* `test_unauthorized_admin_access` — PASS
* `test_create_student` — PASS
* `test_duplicate_register_number` — PASS
* `test_certificate_id_generation` — PASS
* `test_create_and_revoke_certificate` — PASS
* `test_valid_public_verification` — PASS
* `test_revoked_public_verification` — PASS
* `test_not_found_verification` — PASS

**Result**: 11/11 tests passed successfully (0 errors, 0 failures).

---

## 11. ADVANTAGES, LIMITATIONS & FUTURE ENHANCEMENTS

### Advantages
* Instant global verification without institutional delays.
* Elimination of fake certificates via QR verification and central cloud registry.
* Zero storage overhead on web servers due to AWS S3 integration.
* Full audit logging for security compliance.

### Limitations
* Requires internet connectivity for public QR verification.
* Dependent on AWS cloud storage availability.

### Future Enhancements
* **Blockchain Verification**: Store certificate hashes on Ethereum or Polygon blockchain for immutable decentralization.
* **Bulk Certificate Generation**: CSV upload to issue 100+ certificates simultaneously.
* **Email Notification**: Automated email with attached PDF and QR code to students upon issuance.

---

## 12. CONCLUSION
The **Cloud-Based Certificate Verification and Management System Using QR Code** successfully solves credential fraud using modern cloud architecture. By combining Django's secure web framework, AWS S3 cloud storage, dynamic QR generation, and real-time verification logging, the system provides a robust, production-ready solution suitable for college presentation, cloud computing demonstration, and real-world institutional deployment.
