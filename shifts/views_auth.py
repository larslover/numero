# shifts/views_auth.py
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

from .forms import SignupForm
from django.core.mail import send_mail
from django.conf import settings

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Requires admin approval
            user.save()

            messages.success(request, "Account created! Wait for admin approval.")
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})


def custom_login(request):
    print("Login view triggered!")
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('admin:index' if user.is_superuser else "schedule")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


