# 🏥 Smart Hospital Management System (SHMS)

An enterprise-grade, web-based healthcare and clinical administration platform built with **Python 3**, **Django 4.2**, and **Bootstrap 5**. Designed for seamless hospital operations, digital consultation management, electronic medical records (EMR), automated conflict-free appointment scheduling, and multi-medicine digital prescriptions.

---

## 🌟 Key Highlights & Architecture

The system implements a **three-tier Role-Based Access Control (RBAC)** architecture:

```
               ┌──────────────────────────────┐
               │  Smart Hospital Web Platform │
               └──────────────┬───────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐
│  Patient Portal │  │  Doctor Portal  │  │ Admin Dashboard  │
└─────────────────┘  └─────────────────┘  └──────────────────┘
```

1. **Patient Portal**:
   - Patient self-registration with health background, blood group, and emergency contact details.
   - Doctor directory search by specialty and department.
   - Interactive appointment booking with real-time slot conflict prevention.
   - Personal appointment history with status tracking (`Pending`, `Confirmed`, `Completed`, `Cancelled`, `Rejected`).
   - Secure access to digital clinical consultation records and official hospital prescriptions.

2. **Doctor Portal**:
   - Real-time clinical schedule and daily patient queue.
   - One-click confirmation, rejection, or cancellation of booking requests.
   - Full clinical consultation room: records symptoms, formal diagnosis, treatment plan, and follow-up reviews.
   - Dynamic electronic prescription (Rx) generator with multi-item medications (Dosage, Frequency, Duration, Instructions).
   - Assigned patient medical directory and patient clinical histories.
   - Doctor profile and availability toggle.

3. **Hospital Admin Dashboard**:
   - Centralized operational KPI analytics (Total patients, active doctors, clinical departments, appointments, completion rates).
   - Interactive data visualizations with **Chart.js**:
     - *Appointment Status Distribution* (Doughnut chart)
     - *Appointments by Clinical Department* (Bar chart)
     - *7-Day Booking Trends* (Line chart)
   - Doctor Management: Add new doctors with auto-provisioned user accounts, edit credentials, toggle clinic availability, or delete profiles.
   - Patient Directory: Search, edit demographic records, emergency contacts, and blood groups.
   - Department Management: Create and configure clinical disciplines with custom Bootstrap iconography.
   - Appointment & Records oversight.
   - Direct access to Django backend admin at `/admin/`.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3, Django 4.2 LTS |
| **Frontend Framework** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3 |
| **Icons & UI** | Bootstrap Icons 1.11 |
| **Data Visualization**| Chart.js |
| **Database** | SQLite (Production-ready for MySQL / PostgreSQL via `DATABASES` setting) |
| **Authentication** | Django Auth with Custom User Model (`accounts.User`) + RBAC Decorators |
| **Image Processing** | Pillow (PIL) |

---

## 📂 Project Structure

```
Smart Hospital Management System/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
├── config/                 # Project configuration & settings
│   ├── settings.py         # App definitions, media/static paths, AUTH_USER_MODEL
│   ├── urls.py             # Root URL routing & media serving
│   ├── views.py            # Public homepage view
│   ├── wsgi.py
│   └── asgi.py
├── accounts/               # Authentication, Custom User & Role Redirection
│   ├── models.py           # Custom User model (role: ADMIN, DOCTOR, PATIENT)
│   ├── decorators.py       # @patient_required, @doctor_required, @admin_required
│   ├── forms.py            # PatientRegistrationForm, UserLoginForm, UserProfileForm
│   ├── views.py            # Login, registration, dashboard redirect, profile edit
│   └── management/commands/seed_hospital_data.py # Initial database seeder
├── doctors/                # Doctor Profiles & Department Management
│   ├── models.py           # Doctor and Department models
│   ├── forms.py            # DoctorProfileForm, DepartmentForm
│   └── views.py            # Doctor directory, doctor portal views, availability API
├── patients/               # Patient Profiles & Portals
│   ├── models.py           # Patient model (demographics, blood group, allergies)
│   ├── forms.py            # PatientProfileForm
│   └── views.py            # Patient dashboard, appointment history, records & Rx views
├── appointments/           # Scheduling & Slot Conflict Prevention
│   ├── models.py           # Appointment model with DB UniqueConstraint
│   ├── forms.py            # AppointmentBookingForm, AppointmentStatusForm
│   └── views.py            # Booking logic, slot availability JSON API, status manager
├── records/                # EMR & Digital Prescriptions
│   ├── models.py           # MedicalRecord, Prescription, PrescriptionMedicine
│   ├── forms.py            # MedicalRecordForm, PrescriptionMedicineFormSet
│   └── views.py            # Consultation room view, record viewer, printable Rx
├── dashboard/              # Centralized Hospital Admin & Analytics
│   ├── forms.py            # AdminDoctorCreateForm, AdminPatientEditForm
│   ├── views.py            # Analytics overview, Chart.js payloads, CRUD operations
│   └── urls.py
├── templates/              # Clean, modular Bootstrap 5 templates
│   ├── base.html           # Unified responsive navigation & hospital branding
│   ├── home.html           # Public landing page with specialties & hospital stats
│   ├── accounts/           # Login, registration, profile settings
│   ├── doctors/            # Directory, doctor dashboard, schedule, patient records
│   ├── patients/           # Patient dashboard, appointments, records, Rx viewer
│   ├── appointments/       # Interactive slot booking, detail view, cancellation
│   ├── records/            # Clinical consultation room, printable prescription letterhead
│   └── dashboard/          # Admin KPIs, Chart.js graphs, doctor/patient/dept CRUD
└── static/
    └── css/style.css       # Clean healthcare aesthetic, soft teal/blue accents, print stylesheet
```

---

## ⚡ Quick Start & Setup Guide

### 1. Clone & Navigate to Project
```bash
cd "Smart Hospital Management System"
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations & Seed Sample Data
```bash
python manage.py migrate
python manage.py seed_hospital_data
```

### 5. Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Demo Login Accounts

The database comes pre-seeded with sample accounts across all three roles for instant testing and demonstration:

| Portal | Username | Password | Role & Specialty |
| :--- | :--- | :--- | :--- |
| **Admin Operations** | `admin` | `admin123` | System Administrator / Chief Medical Officer |
| **Doctor Portal** | `dr.smith` | `doctor123` | Dr. John Smith (Interventional Cardiology) |
| **Doctor Portal** | `dr.sarah` | `doctor123` | Dr. Sarah Jenkins (Pediatrics) |
| **Doctor Portal** | `dr.patel` | `doctor123` | Dr. Rajesh Patel (Neurology) |
| **Doctor Portal** | `dr.adams` | `doctor123` | Dr. Lisa Adams (General Medicine) |
| **Patient Portal** | `patient1` | `patient123` | Michael Brown (O+, Cardiology visit on file) |
| **Patient Portal** | `patient2` | `patient123` | Emily Davis (A+, General checkup) |
| **Patient Portal** | `patient3` | `patient123` | Robert Wilson (B+, Hypertension consultation) |

*You can also register any new patient account from the registration page at `/accounts/register/`.*

---

## 🔒 Security & Medical Record Privacy Safeguards

- **Access Isolation**: Patients can strictly view only their own medical records, prescriptions, and appointment histories.
- **Doctor Access Scoping**: Doctors are granted access to clinical histories only for patients with active or previous consultations under their care.
- **Atomic Consultation Transactions**: The doctor consultation screen updates the appointment to `Completed`, creates the `MedicalRecord`, and commits all prescribed `PrescriptionMedicine` items within an atomic database transaction (`transaction.atomic()`).
- **Slot Conflict Prevention**: Database-level conditional unique constraints (`unique_active_doctor_appointment`) and view validation prevent double bookings for the same doctor at the same slot.
- **CSRF & XSS Protection**: All forms utilize Django's built-in CSRF token protection and template escaping.

---

## 🧪 Automated Test Suite

Run the full automated test suite covering authentication, RBAC, appointment booking, slot conflict prevention, medical records, and access permissions:

```bash
python manage.py test
```
