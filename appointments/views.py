import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BookingForm, PatientSignupForm
from .models import Appointment, Doctor


def home(request):
    selected = request.GET.get("specialization", "")
    doctors = Doctor.objects.all()
    if selected:
        doctors = doctors.filter(specialization=selected)
    return render(
        request,
        "appointments/home.html",
        {
            "doctors": doctors,
            "specializations": [s[0] for s in Doctor.SPECIALIZATIONS],
            "selected": selected,
        },
    )


def signup(request):
    if request.method == "POST":
        form = PatientSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect("home")
    else:
        form = PatientSignupForm()
    return render(request, "registration/signup.html", {"form": form})


@login_required
def book(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    patient = getattr(request.user, "patient", None)
    if patient is None:
        messages.error(request, "Only patient accounts can book appointments.")
        return redirect("home")

    if request.method == "POST":
        form = BookingForm(request.POST, doctor=doctor)
        if form.is_valid():
            try:
                with transaction.atomic():
                    Appointment.objects.create(
                        doctor=doctor,
                        patient=patient,
                        date=form.cleaned_data["date"],
                        slot=form.cleaned_data["slot"],
                    )
            except IntegrityError:
                form.add_error(None, "That slot was just booked by someone else. Please pick another.")
            else:
                messages.success(request, "Your appointment is booked!")
                return redirect("my_appointments")
    else:
        form = BookingForm(doctor=doctor)

    return render(request, "appointments/book.html", {"form": form, "doctor": doctor})


@login_required
def my_appointments(request):
    patient = getattr(request.user, "patient", None)
    appointments = patient.appointments.select_related("doctor") if patient else []
    return render(request, "appointments/my_appointments.html", {"appointments": appointments})


@login_required
@require_POST
def cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, patient__user=request.user)
    appointment.status = Appointment.Status.CANCELLED
    appointment.save()
    messages.info(request, "Appointment cancelled.")
    return redirect("my_appointments")


@login_required
def doctor_dashboard(request):
    doctor = getattr(request.user, "doctor", None)
    if doctor is None:
        messages.error(request, "This page is only for doctors.")
        return redirect("home")

    today = datetime.date.today()
    todays = (
        doctor.appointments.filter(date=today)
        .exclude(status=Appointment.Status.CANCELLED)
        .select_related("patient__user")
    )
    upcoming = (
        doctor.appointments.filter(date__gt=today)
        .exclude(status=Appointment.Status.CANCELLED)
        .select_related("patient__user")[:10]
    )
    return render(
        request,
        "appointments/doctor_dashboard.html",
        {"doctor": doctor, "today": today, "todays": todays, "upcoming": upcoming},
    )


@login_required
@require_POST
def mark_completed(request, pk):
    doctor = getattr(request.user, "doctor", None)
    appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    appointment.status = Appointment.Status.COMPLETED
    appointment.save()
    return redirect("doctor_dashboard")
