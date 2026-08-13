# Cloud-Based Certificate Verification and Management System Using QR Code

A production-style, full-stack Cloud Computing application built with **Python**, **Django**, **AWS S3 Storage**, **PostgreSQL**, and **QR Code Technology**.

---

## 🌟 Key Features

* **Cloud File Storage Integration**: Certificate PDF/Image documents and generated QR codes are stored securely in **AWS S3 Bucket**.
* **Automatic Unique Certificate ID Generation**: Automatic server-side formatting (`CERT-YYYY-XXXXX`) preventing duplicate IDs.
* **Real-time QR Code Generation**: Python `qrcode` dynamically generates encrypted QR codes pointing directly to public server verification endpoints (`/verify/CERT-2026-00001/`).
* **Public Certificate Verification**: No login required. Anyone can verify certificate authenticity by entering a Certificate ID or scanning the QR code.
* **Role-Based Access Control**:
  * **Administrator**: Manage students, issue certificates, upload documents to cloud, revoke/restore certificates, and view real-time audit logs.
  * **Student**: View personal dashboard, inspect issued certificates, view QR codes, and download original files.
  * **Public**: Instant verification returning `VALID`, `REVOKED`, `EXPIRED`, or `NOT_FOUND`.
* **Audit & Verification Logging**: Automatically logs every verification attempt capturing IP address, timestamp, User Agent, and result status.
* **Security & Validation**: File type validation (PDF, PNG, JPG, JPEG), file size cap (10MB), CSRF protection, and password hashing.
* **Modern Aesthetic UI**: Dark Navy + Gold theme built with Bootstrap 5 and Bootstrap Icons.

---

## 🛠️ Technology Stack

* **Backend**: Python 3.13, Django 5.2, Django ORM, Django Authentication, Django REST Framework
* **Frontend**: HTML5, CSS3, Bootstrap 5, Bootstrap Icons, JavaScript (ES6)
* **Cloud Storage**: AWS S3 (`boto3`, `django-storages`)
* **Database**: SQLite (Development) / PostgreSQL (Production ready via `dj-database-url` & `psycopg`)
* **QR Generator**: `qrcode[pil]`
* **Environment Configuration**: `python-dotenv`

---

## 📂 Project Structure

```text
certificate_verification/
│
├── manage.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── COLLEGE_DOCUMENTATION.md
├── PRESENTATION_SLIDES.md
│
├── config/                  # Django Core Configuration
│   ├── settings.py
│   ├── urls.py
│   ├── views.py             # Custom 400/403/404/500 error handlers
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                # User & Student Authentication
│   ├── models.py            # Student Profile linked to Django User
│   ├── forms.py             # Login & Student Forms
│   ├── views.py
│   └── urls.py
│
├── certificates/            # Certificate Management & QR Generation
│   ├── models.py            # Certificate Model
│   ├── utils.py             # ID Generator & QR Generator
│   ├── forms.py             # Certificate Form with File Validation
│   ├── views.py             # Admin Dashboard, Student CRUD, Cert CRUD
│   ├── urls.py
│   └── management/
│       └── commands/
│           └── seed_data.py # Sample data seeder
│
├── verification/            # Public Verification & Audit Logs
│   ├── models.py            # VerificationLog Model
│   ├── views.py             # Public verification & log recorder
│   └── urls.py
│
├── templates/               # Reusable HTML Templates
│   ├── base.html
│   ├── home.html
│   ├── about.html
│   ├── 400.html, 403.html, 404.html, 500.html
│   ├── accounts/
│   ├── certificates/
│   └── verification/
│
├── static/                  # Dark Navy + Gold Theme Styling
│   ├── css/style.css
│   └── js/main.js
│
└── tests/                   # Automated Unit Tests
    └── test_all.py
```

---

## 🚀 Quick Start (Local Windows Setup)

### 1. Environment Setup
Open PowerShell inside the project directory:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:

```env
SECRET_KEY=django-insecure-dev-key-2026-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1
```

### 4. Database Migrations & Seed Sample Data
```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py seed_data
```

This creates 5 sample students and 5 sample certificates automatically!
Default login credentials:
* **Admin**: Username: `admin` | Password: `admin123`
* **Student**: Username: `john_doe` | Password: `Student123!`

### 5. Run Server
```powershell
python manage.py runserver
```

Open your browser at `http://127.0.0.1:8000/`.

---

## ☁️ AWS S3 Cloud Storage Integration

To enable AWS S3 Cloud Storage:

1. Create an AWS S3 Bucket on AWS Console.
2. Update `.env`:
   ```env
   USE_S3=True
   AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY
   AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY
   AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name
   AWS_S3_REGION_NAME=us-east-1
   ```
3. Restart server. All uploaded certificate documents and generated QR codes will be stored in AWS S3 automatically!

---

## 🧪 Running Automated Tests

Run all 11 unit tests covering Authentication, Student Management, Certificate ID Generation, QR Creation, Revocation, and Public Verification:

```powershell
python manage.py test tests
```

---

## 🌐 Deployment to Render / Cloud Platform

1. Provision a PostgreSQL Database on Render.
2. Create an AWS S3 Bucket for Media Files.
3. Push codebase to GitHub.
4. Connect repository to Render as a Web Service.
5. Set Environment Variables in Render Dashboard (`DATABASE_URL`, `SECRET_KEY`, `USE_S3=True`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`).
6. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
7. Start Command: `gunicorn config.wsgi:application`
