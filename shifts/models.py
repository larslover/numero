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
class TimeSlot(models.Model):
    label = models.CharField(_("Tidspunkt"), max_length=50, unique=True)  # e.g., "8:00–10:00"
    is_weekend = models.BooleanField(_("Helg?"), default=False)
    order = models.PositiveIntegerField(_("Rekkefølge"), default=0)

    class Meta:
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


class ShiftAssignment(models.Model):
    ROLE_CHOICES = [
        ('worker', _("Ansatt")),
        ('volunteer', _("Frivillig")),
    ]

    user = models.ForeignKey(User, verbose_name=_("Bruker"), on_delete=models.CASCADE)
    date = models.DateField(_("Dato"))
    time_slot = models.ForeignKey(TimeSlot, verbose_name=_("Tidsluke"), on_delete=models.CASCADE)
    role = models.CharField(_("Rolle"), max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'date', 'time_slot', 'role')
        verbose_name = _("Vakt")
        verbose_name_plural = _("Vakter")

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
