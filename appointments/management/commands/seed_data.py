import datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from appointments.models import Appointment, Doctor, Patient

DOCTORS = [
    ("dr_ananya", "Ananya Rao", "Cardiology", 800),
    ("dr_ravi", "Ravi Teja", "Dermatology", 500),
    ("dr_meera", "Meera Nair", "Neurology", 900),
    ("dr_karthik", "Karthik Reddy", "Orthopedics", 700),
    ("dr_sneha", "Sneha Iyer", "Pediatrics", 450),
    ("dr_arjun", "Arjun Varma", "General Medicine", 300),
]


class Command(BaseCommand):
    help = "Create sample doctors and a demo patient"

    def handle(self, *args, **options):
        for username, name, spec, fee in DOCTORS:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password("doctor123")
                user.save()
            Doctor.objects.get_or_create(
                user=user, defaults={"name": name, "specialization": spec, "fee": fee}
            )

        patient_user, created = User.objects.get_or_create(
            username="patient1", defaults={"first_name": "Demo Patient"}
        )
        if created:
            patient_user.set_password("patient123")
            patient_user.save()
        patient, _ = Patient.objects.get_or_create(
            user=patient_user, defaults={"age": 21, "phone": "9876543210"}
        )

        first_doctor = Doctor.objects.get(user__username="dr_ananya")
        Appointment.objects.get_or_create(
            doctor=first_doctor,
            date=datetime.date.today(),
            slot="10:00",
            defaults={"patient": patient},
        )

        self.stdout.write(self.style.SUCCESS("Sample data created."))
        self.stdout.write("Doctor logins : dr_ananya / doctor123 (also dr_ravi, dr_meera, ...)")
        self.stdout.write("Patient login : patient1 / patient123")