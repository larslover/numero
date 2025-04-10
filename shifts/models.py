from django.db import models
from django.contrib.auth.models import User
# models.py

class TimeSlot(models.Model):
    label = models.CharField(max_length=50, unique=True)  # e.g., "8:00–10:00"
    is_weekend = models.BooleanField(default=False)       # distinguishes Saturday from weekdays
    order = models.PositiveIntegerField(default=0)         # for sorting

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.label

class VolunteerLimit(models.Model):
    date = models.DateField(unique=True)
    limit = models.PositiveIntegerField(default=2)

    def __str__(self):
        return f"{self.date} - {self.limit} volunteers"

class ShiftAssignment(models.Model):
    ROLE_CHOICES = [
        ('worker', 'Worker'),
        ('volunteer', 'Volunteer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'date', 'time_slot', 'role')

    def __str__(self):
        return f"{self.user.username} as {self.role} on {self.date} at {self.time_slot}"
# models.py

