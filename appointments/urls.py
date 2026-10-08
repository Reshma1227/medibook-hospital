from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("book/<int:doctor_id>/", views.book, name="book"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
    path("cancel/<int:pk>/", views.cancel, name="cancel"),
    path("doctor/dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("doctor/complete/<int:pk>/", views.mark_completed, name="mark_completed"),
]