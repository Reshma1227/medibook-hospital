from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class Doctor(models.Model):
    SPECIALIZATIONS = [
        ("Cardiology", "Cardiology"),
        ("Dermatology", "Dermatology"),
        ("Neurology", "Neurology"),
        ("Orthopedics", "Orthopedics"),
        ("Pediatrics", "Pediatrics"),
        ("General Medicine", "General Medicine"),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATIONS)
    fee = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["specialization", "name"]

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Appointment(models.Model):
    class Slot(models.TextChoices):
        S1 = "09:00", "09:00 AM"
        S2 = "10:00", "10:00 AM"
        S3 = "11:00", "11:00 AM"
        S4 = "12:00", "12:00 PM"
        S5 = "14:00", "02:00 PM"
        S6 = "15:00", "03:00 PM"
        S7 = "16:00", "04:00 PM"
        S8 = "17:00", "05:00 PM"

    class Status(models.TextChoices):
        BOOKED = "Booked", "Booked"
        COMPLETED = "Completed", "Completed"
        CANCELLED = "Cancelled", "Cancelled"

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="appointments")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateField()
    slot = models.CharField(max_length=5, choices=Slot.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.BOOKED)

    class Meta:
        ordering = ["date", "slot"]
        constraints = [
            # Same doctor + date + slot can only exist once (cancelled ones are ignored)
            models.UniqueConstraint(
                fields=["doctor", "date", "slot"],
                condition=~Q(status="Cancelled"),
                name="unique_active_doctor_date_slot",
            )
        ]

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.date} at {self.slot}"