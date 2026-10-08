import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Appointment, Patient


class PatientSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, label="Full name")
    age = forms.IntegerField(min_value=0, max_value=120)
    phone = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ["username", "first_name", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Patient.objects.create(
                user=user,
                age=self.cleaned_data["age"],
                phone=self.cleaned_data["phone"],
            )
        return user


class BookingForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    slot = forms.ChoiceField(choices=Appointment.Slot.choices)

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctor = doctor
        self.fields["date"].widget.attrs["min"] = datetime.date.today().isoformat()

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date < datetime.date.today():
            raise forms.ValidationError("You cannot book an appointment in the past.")
        return date

    def clean(self):
        cleaned = super().clean()
        date, slot = cleaned.get("date"), cleaned.get("slot")
        if date and slot and self.doctor:
            taken = (
                Appointment.objects.filter(doctor=self.doctor, date=date, slot=slot)
                .exclude(status=Appointment.Status.CANCELLED)
                .exists()
            )
            if taken:
                raise forms.ValidationError(
                    "Sorry, that time slot is already booked for this doctor. "
                    "Please choose a different slot or date."
                )
        return cleaned