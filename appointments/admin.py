from django.contrib import admin

from .models import Appointment, Doctor, Patient


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "specialization", "fee", "user")
    list_filter = ("specialization",)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("user", "age", "phone")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "date", "slot", "status")
    list_filter = ("status", "date", "doctor")