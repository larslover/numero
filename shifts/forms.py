from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import ShiftAssignment
class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]  # Use built-in password fields

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False  # Mark new users as inactive (requires admin approval)
        if commit:
            user.save()
        return user
# forms.py


class ShiftAssignmentForm(forms.ModelForm):
    class Meta:
        model = ShiftAssignment
        fields = ['date', 'time_slot', 'role']  # Include the fields you want the user to input

    # Optionally, you can add custom validation or modify the behavior of the form
