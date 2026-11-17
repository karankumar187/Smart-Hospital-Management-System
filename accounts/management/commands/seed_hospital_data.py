from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta
from accounts.models import User
from doctors.models import Department, Doctor
from patients.models import Patient
from appointments.models import Appointment
from records.models import MedicalRecord, Prescription, PrescriptionMedicine

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds initial realistic data for Smart Hospital Management System"

    def handle(self, *args, **options):
        self.stdout.write("Starting hospital database seeding...")

        # 1. Administrator User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@smarthospital.org',
                'first_name': 'Chief',
                'last_name': 'Administrator',
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone': '+1 (800) 555-0100',
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created Superuser / Admin: admin / admin123"))
        else:
            self.stdout.write("Admin user already exists.")

        # 2. Departments
        departments_data = [
            {
                'name': 'Cardiology',
                'description': 'Comprehensive cardiovascular care including interventional cardiology, heart failure management, echocardiography, and arrhythmia care.',
                'icon': 'bi-heart-pulse'
            },
            {
                'name': 'Neurology',
                'description': 'Advanced evaluation and therapy for central and peripheral nervous system disorders, stroke management, and epilepsy care.',
                'icon': 'bi-activity'
            },
            {
                'name': 'Pediatrics',
                'description': 'Dedicated healthcare for infants, children, and adolescents focusing on preventive wellness, vaccination, and acute pediatric illnesses.',
                'icon': 'bi-emoji-smile'
            },
            {
                'name': 'Orthopedics',
                'description': 'Surgical and non-surgical treatment of musculoskeletal system diseases, joint replacement, sports injuries, and trauma rehabilitation.',
                'icon': 'bi-bandaid'
            },
            {
                'name': 'Dermatology',
                'description': 'Specialized clinical and cosmetic dermatology covering skin cancer screening, eczema, psoriasis, acne management, and dermatologic surgeries.',
                'icon': 'bi-stars'
            },
            {
                'name': 'General Medicine',
                'description': 'Primary care and internal medicine managing chronic lifestyle conditions like hypertension, diabetes, and infectious illnesses.',
                'icon': 'bi-capsule'
            },
        ]

        dept_objs = {}
        for d_data in departments_data:
            dept, _ = Department.objects.get_or_create(
                name=d_data['name'],
                defaults={
                    'description': d_data['description'],
                    'icon': d_data['icon'],
                    'is_active': True
                }
            )
            dept_objs[dept.name] = dept
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(dept_objs)} clinical departments."))

        # 3. Doctors
        doctors_data = [
            {
                'username': 'dr.smith',
                'first_name': 'John',
                'last_name': 'Smith',
                'email': 'dr.smith@smarthospital.org',
                'phone': '+1 (800) 555-0111',
                'department': dept_objs['Cardiology'],
                'specialization': 'Interventional Cardiologist',
                'qualification': 'MD, FACC, FSCAI',
                'experience_years': 14,
                'consultation_fee': 95.00,
                'room_number': 'Suite 101, Cardio Wing',
                'bio': 'Board-certified interventional cardiologist with over 14 years of clinical experience in coronary angiography, angioplasty, and preventative cardiology.'
            },
            {
                'username': 'dr.sarah',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'email': 'dr.jenkins@smarthospital.org',
                'phone': '+1 (800) 555-0112',
                'department': dept_objs['Pediatrics'],
                'specialization': 'Consultant Pediatrician',
                'qualification': 'MD (Pediatrics), FAAP',
                'experience_years': 9,
                'consultation_fee': 60.00,
                'room_number': 'Room 204, Child Care Pavilion',
                'bio': 'Specializing in neonatal care, child development milestones, pediatric nutritional counseling, and childhood immunizations.'
            },
            {
                'username': 'dr.patel',
                'first_name': 'Rajesh',
                'last_name': 'Patel',
                'email': 'dr.patel@smarthospital.org',
                'phone': '+1 (800) 555-0113',
                'department': dept_objs['Neurology'],
                'specialization': 'Clinical Neurologist & Neurophysiologist',
                'qualification': 'MBBS, MD, DM (Neurology)',
                'experience_years': 16,
                'consultation_fee': 110.00,
                'room_number': 'Suite 302, Neuro Sciences',
                'bio': 'Extensive clinical background treating stroke rehabilitation, migraine disorders, neurodegenerative conditions, and peripheral neuropathies.'
            },
            {
                'username': 'dr.chen',
                'first_name': 'Emily',
                'last_name': 'Chen',
                'email': 'dr.chen@smarthospital.org',
                'phone': '+1 (800) 555-0114',
                'department': dept_objs['Orthopedics'],
                'specialization': 'Orthopedic & Joint Surgeon',
                'qualification': 'MS (Ortho), Fellowship in Arthroscopy',
                'experience_years': 11,
                'consultation_fee': 85.00,
                'room_number': 'Suite 105, Ortho Clinic',
                'bio': 'Expert in minimally invasive joint surgery, sports ligament reconstruction, fracture management, and osteoarthritic therapies.'
            },
            {
                'username': 'dr.miller',
                'first_name': 'David',
                'last_name': 'Miller',
                'email': 'dr.miller@smarthospital.org',
                'phone': '+1 (800) 555-0115',
                'department': dept_objs['Dermatology'],
                'specialization': 'Dermatologist & Laser Specialist',
                'qualification': 'MD (Dermatology)',
                'experience_years': 8,
                'consultation_fee': 70.00,
                'room_number': 'Room 208, Skin Care Center',
                'bio': 'Focusing on autoimmune dermatoses, clinical laser therapies, contact allergy diagnostics, and restorative skin treatments.'
            },
            {
                'username': 'dr.adams',
                'first_name': 'Lisa',
                'last_name': 'Adams',
                'email': 'dr.adams@smarthospital.org',
                'phone': '+1 (800) 555-0116',
                'department': dept_objs['General Medicine'],
                'specialization': 'Internal Medicine Physician',
                'qualification': 'MBBS, MD (General Medicine)',
                'experience_years': 12,
                'consultation_fee': 50.00,
                'room_number': 'Room 102, Outpatient Department',
                'bio': 'Passionate about comprehensive preventative health screenings, chronic disease prevention, hypertension, and metabolic syndrome care.'
            },
        ]

        doctor_objs = []
        for doc_data in doctors_data:
            user, u_created = User.objects.get_or_create(
                username=doc_data['username'],
                defaults={
                    'email': doc_data['email'],
                    'first_name': doc_data['first_name'],
                    'last_name': doc_data['last_name'],
                    'phone': doc_data['phone'],
                    'role': User.ROLE_DOCTOR,
                    'is_staff': False
                }
            )
            if u_created:
                user.set_password('doctor123')
                user.save()

            doctor, _ = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'department': doc_data['department'],
                    'specialization': doc_data['specialization'],
                    'qualification': doc_data['qualification'],
                    'experience_years': doc_data['experience_years'],
                    'consultation_fee': doc_data['consultation_fee'],
                    'room_number': doc_data['room_number'],
                    'bio': doc_data['bio'],
                    'is_available': True,
                    'working_days': 'Monday, Tuesday, Wednesday, Thursday, Friday',
                    'working_hours_start': time(9, 0),
                    'working_hours_end': time(17, 0),
                }
            )
            doctor_objs.append(doctor)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(doctor_objs)} doctors (Logins: dr.smith, dr.sarah, dr.patel, etc. / Password: doctor123)"))

        # 4. Patients
        patients_data = [
            {
                'username': 'patient1',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'email': 'michael.brown@example.com',
                'phone': '+1 (555) 019-1001',
                'dob': date(1990, 5, 14),
                'gender': 'Male',
                'blood_group': 'O+',
                'address': '742 Evergreen Terrace, Springfield',
                'emergency_contact_name': 'Laura Brown (Spouse)',
                'emergency_contact_phone': '+1 (555) 019-1009',
                'medical_history': 'Occasional seasonal allergies; mild exercise-induced asthma managed with inhaler.'
            },
            {
                'username': 'patient2',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'email': 'emily.davis@example.com',
                'phone': '+1 (555) 019-1002',
                'dob': date(1995, 8, 22),
                'gender': 'Female',
                'blood_group': 'A+',
                'address': '456 Elmwood Avenue, North Hills',
                'emergency_contact_name': 'Thomas Davis (Father)',
                'emergency_contact_phone': '+1 (555) 019-1008',
                'medical_history': 'No known allergies or chronic conditions.'
            },
            {
                'username': 'patient3',
                'first_name': 'Robert',
                'last_name': 'Wilson',
                'email': 'robert.wilson@example.com',
                'phone': '+1 (555) 019-1003',
                'dob': date(1972, 11, 30),
                'gender': 'Male',
                'blood_group': 'B+',
                'address': '12 Oak Ridge Lane, Lakeview',
                'emergency_contact_name': 'Sarah Wilson (Daughter)',
                'emergency_contact_phone': '+1 (555) 019-1007',
                'medical_history': 'Essential hypertension diagnosed 2018; Penicillin allergy.'
            },
            {
                'username': 'patient4',
                'first_name': 'Sophia',
                'last_name': 'Martinez',
                'email': 'sophia.martinez@example.com',
                'phone': '+1 (555) 019-1004',
                'dob': date(2001, 3, 10),
                'gender': 'Female',
                'blood_group': 'AB-',
                'address': '88 Maple Boulevard, Riverdale',
                'emergency_contact_name': 'Elena Martinez (Mother)',
                'emergency_contact_phone': '+1 (555) 019-1006',
                'medical_history': 'Mild eczema.'
            },
            {
                'username': 'patient5',
                'first_name': 'James',
                'last_name': 'Anderson',
                'email': 'james.anderson@example.com',
                'phone': '+1 (555) 019-1005',
                'dob': date(1982, 1, 19),
                'gender': 'Male',
                'blood_group': 'O-',
                'address': '304 Birch Road, Summit Valley',
                'emergency_contact_name': 'Karen Anderson (Wife)',
                'emergency_contact_phone': '+1 (555) 019-1011',
                'medical_history': 'Previous right ACL reconstruction in 2015.'
            }
        ]

        patient_objs = []
        for p_data in patients_data:
            user, u_created = User.objects.get_or_create(
                username=p_data['username'],
                defaults={
                    'email': p_data['email'],
                    'first_name': p_data['first_name'],
                    'last_name': p_data['last_name'],
                    'phone': p_data['phone'],
                    'role': User.ROLE_PATIENT,
                    'is_staff': False
                }
            )
            if u_created:
                user.set_password('patient123')
                user.save()

            patient, _ = Patient.objects.get_or_create(
                user=user,
                defaults={
                    'dob': p_data['dob'],
                    'gender': p_data['gender'],
                    'blood_group': p_data['blood_group'],
                    'address': p_data['address'],
                    'emergency_contact_name': p_data['emergency_contact_name'],
                    'emergency_contact_phone': p_data['emergency_contact_phone'],
                    'medical_history': p_data['medical_history'],
                }
            )
            patient_objs.append(patient)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(patient_objs)} patients (Logins: patient1 through patient5 / Password: patient123)"))

        # 5. Appointments, Medical Records & Prescriptions
        today = date.today()

        # A) Completed Consultation with Dr. Smith & Patient 1 (Past)
        appt1, _ = Appointment.objects.get_or_create(
            patient=patient_objs[0],
            doctor=doctor_objs[0],
            appointment_date=today - timedelta(days=5),
            appointment_time=time(9, 30),
            defaults={
                'status': Appointment.STATUS_COMPLETED,
                'reason': 'Experiencing persistent palpitations after routine exercise and occasional shortness of breath.',
                'doctor_notes': '12-lead ECG normal. Resting HR 76 bpm. Advised 24-hr Holter monitor and echocardiogram review.'
            }
        )

        rec1, rec1_created = MedicalRecord.objects.get_or_create(
            appointment=appt1,
            defaults={
                'patient': patient_objs[0],
                'doctor': doctor_objs[0],
                'diagnosis': 'Benign Sinus Tachycardia & Exercise-related palpitations',
                'symptoms': 'Intermittent palpitation sensation, heart rate up to 110 bpm at mild exertion, no syncope or chest pressure.',
                'treatment': 'Oral beta-blocker therapy at low dose; adequate hydration; restriction of caffeine and energy drinks.',
                'notes': 'Follow up in 2 weeks with completed Holter log.',
                'follow_up_date': today + timedelta(days=9)
            }
        )

        if rec1_created or not hasattr(rec1, 'prescription'):
            rx1 = Prescription.objects.create(
                medical_record=rec1,
                patient=patient_objs[0],
                doctor=doctor_objs[0],
                notes='Take medications with water after breakfast. Avoid excessive coffee and strenuous high-intensity interval training until review.'
            )
            PrescriptionMedicine.objects.create(
                prescription=rx1,
                medicine_name='Metoprolol Tartrate',
                dosage='25 mg',
                frequency='Once daily in morning',
                duration='14 days',
                instructions='Take with or immediately after food'
            )
            PrescriptionMedicine.objects.create(
                prescription=rx1,
                medicine_name='Multivitamin Co-Enzyme Q10',
                dosage='1 Capsule',
                frequency='Once daily',
                duration='30 days',
                instructions='Take after lunch'
            )

        # B) Completed Consultation with Dr. Adams & Patient 3 (Past)
        appt2, _ = Appointment.objects.get_or_create(
            patient=patient_objs[2],
            doctor=doctor_objs[5],
            appointment_date=today - timedelta(days=2),
            appointment_time=time(10, 0),
            defaults={
                'status': Appointment.STATUS_COMPLETED,
                'reason': 'Follow-up for routine blood pressure management and lab work review.',
                'doctor_notes': 'BP measured 138/88 mmHg. Weight stable. Labs show normal renal panel.'
            }
        )

        rec2, rec2_created = MedicalRecord.objects.get_or_create(
            appointment=appt2,
            defaults={
                'patient': patient_objs[2],
                'doctor': doctor_objs[5],
                'diagnosis': 'Stage 1 Essential Hypertension (Well Controlled)',
                'symptoms': 'Occasional morning occipital tension, no visual disturbances or pedal edema.',
                'treatment': 'Continue ACE-inhibitor regimen; low-sodium DASH diet; 30 mins brisk walking 5 days a week.',
                'notes': 'Patient reminded of penicillin allergy. Blood pressure log maintained appropriately.',
                'follow_up_date': today + timedelta(days=30)
            }
        )

        if rec2_created or not hasattr(rec2, 'prescription'):
            rx2 = Prescription.objects.create(
                medical_record=rec2,
                patient=patient_objs[2],
                doctor=doctor_objs[5],
                notes='Maintain daily blood pressure log in morning and evening. Reduce table salt consumption.'
            )
            PrescriptionMedicine.objects.create(
                prescription=rx2,
                medicine_name='Lisinopril Tablets',
                dosage='10 mg',
                frequency='Once daily in morning',
                duration='30 days',
                instructions='Take at consistent time every day'
            )
            PrescriptionMedicine.objects.create(
                prescription=rx2,
                medicine_name='Amlodipine Besylate',
                dosage='5 mg',
                frequency='Once daily at night',
                duration='30 days',
                instructions='Take before sleep'
            )

        # C) Today's Appointments (Confirmed)
        Appointment.objects.get_or_create(
            patient=patient_objs[1],
            doctor=doctor_objs[0],
            appointment_date=today,
            appointment_time=time(10, 30),
            defaults={
                'status': Appointment.STATUS_CONFIRMED,
                'reason': 'Annual cardiovascular checkup and ECG screening.',
                'doctor_notes': 'Confirmed via reception desk.'
            }
        )

        Appointment.objects.get_or_create(
            patient=patient_objs[3],
            doctor=doctor_objs[4],
            appointment_date=today,
            appointment_time=time(14, 0),
            defaults={
                'status': Appointment.STATUS_CONFIRMED,
                'reason': 'Persistent red rash on forearm and allergic contact dermatitis check.',
                'doctor_notes': 'Slot locked for dermatoscopy.'
            }
        )

        # D) Upcoming Pending Appointments (Tomorrow & Future)
        Appointment.objects.get_or_create(
            patient=patient_objs[0],
            doctor=doctor_objs[3],
            appointment_date=today + timedelta(days=1),
            appointment_time=time(11, 0),
            defaults={
                'status': Appointment.STATUS_PENDING,
                'reason': 'Knee pain and stiffness after running 5k last weekend.'
            }
        )

        Appointment.objects.get_or_create(
            patient=patient_objs[4],
            doctor=doctor_objs[0],
            appointment_date=today + timedelta(days=2),
            appointment_time=time(11, 30),
            defaults={
                'status': Appointment.STATUS_PENDING,
                'reason': 'High blood pressure reading during workplace health fair.'
            }
        )

        Appointment.objects.get_or_create(
            patient=patient_objs[1],
            doctor=doctor_objs[1],
            appointment_date=today + timedelta(days=3),
            appointment_time=time(15, 0),
            defaults={
                'status': Appointment.STATUS_CONFIRMED,
                'reason': 'Routine pediatric developmental checkup and vaccine consultation.'
            }
        )

        self.stdout.write(self.style.SUCCESS("Seeded sample appointments across past, today, and future dates with attached medical records and prescriptions!"))
        self.stdout.write(self.style.SUCCESS("\nSmart Hospital seeding complete!"))
