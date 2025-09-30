# models.py
from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.models import User

class Shift(models.Model):
    date = models.DateField()
    time_slot = models.CharField(max_length=100)  # E.g., "12:00 PM - 1:00 PM"
    workers = models.ManyToManyField(User, related_name='assigned_shifts')

    def __str__(self):
        return f"{self.date} - {self.time_slot}"

    class Meta:
        verbose_name = "Vakt"
        verbose_name_plural = "Vakter"

class TimeSlot(models.Model):
    label = models.CharField(_("Tidspunkt"), max_length=50)  # Remove unique=True
    is_weekend = models.BooleanField(_("Helg?"), default=False)
    order = models.PositiveIntegerField(_("Rekkefølge"), default=0)

    class Meta:
        unique_together = ['label', 'is_weekend']  # Ensure uniqueness for the combination of label and is_weekend
        ordering = ['order']
        verbose_name = _("Tidsluke")
        verbose_name_plural = _("Tidsluker")

    def __str__(self):
        return self.label


class VolunteerLimit(models.Model):
    date = models.DateField(_("Dato"), unique=True)
    limit = models.PositiveIntegerField(_("Grense for frivillige"), default=2)

    class Meta:
        verbose_name = _("Frivilliggrense")
        verbose_name_plural = _("Frivilliggrenser")

    def __str__(self):
        return f"{self.date} - {self.limit} frivillige"

from django.core.exceptions import ValidationError
class ShiftAssignment(models.Model):
    ROLE_CHOICES = [
        ('worker', "Ansatt"),
        ('volunteer', "Frivillig"),
    ]

    user = models.ForeignKey(User, verbose_name="Bruker", on_delete=models.CASCADE)
    date = models.DateField("Dato")
    time_slot = models.ForeignKey(TimeSlot, verbose_name="Tidsluke", on_delete=models.CASCADE)
    role = models.CharField("Rolle", max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'date', 'time_slot', 'role')
        verbose_name = "Vaktoppgave"
        verbose_name_plural = "Vaktoppgaver"

    def clean(self):
        # Check for double booking
        other_role = 'volunteer' if self.role == 'worker' else 'worker'
        exists = ShiftAssignment.objects.filter(
            user=self.user,
            date=self.date,
            time_slot=self.time_slot,
            role=other_role
        ).exists()

        if exists:
            raise ValidationError(f"{self.user.username} is already assigned as {other_role} for this slot.")

    def save(self, *args, **kwargs):
        self.clean()  # enforce validation
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} som {self.get_role_display()} {self.date} kl. {self.time_slot}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('worker', 'Worker'),
        ('volunteer', 'Volunteer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User model
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)  # Can be Worker or Volunteer
    bio = models.TextField(blank=True, null=True)  # Optional additional info about the user
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional contact number

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
