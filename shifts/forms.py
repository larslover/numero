from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import ShiftAssignment, TimeSlot
import datetime
from django.contrib import admin



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



class ShiftAssignmentForm(forms.ModelForm):
    class Meta:
        model = ShiftAssignment
        fields = '__all__'

    class Media:
        js = ('shifts/js/time_slot_dynamic.js',)  # this is your custom JS


class ShiftAssignmentAdmin(admin.ModelAdmin):
    form = ShiftAssignmentForm
    list_display = ("user", "date", "time_slot", "role")
    list_filter = ("date", "time_slot", "role")
    search_fields = ("user__username", "date", "time_slot")
    ordering = ("date", "time_slot")

    readonly_fields = ("user", "date", "time_slot", "role")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


