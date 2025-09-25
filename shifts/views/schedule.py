from datetime import datetime, timedelta
from django.shortcuts import render
from shifts.models import VolunteerLimit, ShiftAssignment, TimeSlot
from django.contrib.auth.models import User
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
@login_required
def my_bookings(request):
    today = timezone.now().date()

    # Grab upcoming and past separately
    upcoming_shifts = (
        ShiftAssignment.objects.filter(user=request.user, date__gte=today)
        .order_by("date", "time_slot")
    )
    past_shifts = (
        ShiftAssignment.objects.filter(user=request.user, date__lt=today)
        .order_by("-date", "time_slot")  # show most recent first
    )

    return render(
        request,
        "shifts/my_bookings.html",
        {
            "upcoming_shifts": upcoming_shifts,
            "past_shifts": past_shifts,
        },
    )

logger = logging.getLogger(__name__)

# Pull time slots from DB
weekday_times = TimeSlot.objects.filter(is_weekend=False)
saturday_times = TimeSlot.objects.filter(is_weekend=True)
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from shifts.models import TimeSlot, ShiftAssignment, VolunteerLimit

@login_required
def schedule_view(request, week_offset=0):
    week_offset = int(week_offset)
    today = datetime.now()
    target_week = today + timedelta(weeks=week_offset)
    start_of_week = target_week - timedelta(days=target_week.weekday())

    # Prepare shifts
    shifts = []
    shift_map = {}
    

    # Weekdays (Monday to Friday)
    weekdays_combined = [
        ((start_of_week + timedelta(days=i)).strftime("%A"),
         (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d"))
        for i in range(5)
    ]

    # Time slots
    weekday_time_slots = TimeSlot.objects.filter(is_weekend=False)
    saturday_time_slots = TimeSlot.objects.filter(is_weekend=True)

    # Volunteer limits
    volunteer_limits = {
        obj.date.strftime("%Y-%m-%d"): obj.limit
        for obj in VolunteerLimit.objects.all()
    }

    # Workers for admin sidebar
    workers_for_admin = User.objects.filter(userprofile__role='worker') if request.user.is_staff else []

    # Helper to build shift info
    def build_shift(date, time_slot):
        assignments = ShiftAssignment.objects.filter(date=date, time_slot=time_slot)
        volunteers = [a.user.username for a in assignments if a.role == "volunteer"]
        workers = [a.user.username for a in assignments if a.role == "worker"]
        shift_info = {
            "date": date.strftime("%Y-%m-%d"),
            "time_slot": time_slot,
            "users": volunteers,
            "workers": workers,
            "max_slots": volunteer_limits.get(date.strftime("%Y-%m-%d"), 2),
        }
        return shift_info

    # Weekday shifts
    for i in range(5):
        date = start_of_week + timedelta(days=i)
        for time_slot in weekday_time_slots:
            shift_info = build_shift(date, time_slot)
            shifts.append(shift_info)
            shift_map[f"{shift_info['date']}|{time_slot.label}"] = shift_info

    # Saturday shifts
    saturday_date = start_of_week + timedelta(days=5)
    for time_slot in saturday_time_slots:
        shift_info = build_shift(saturday_date, time_slot)
        shifts.append(shift_info)
        shift_map[f"{shift_info['date']}|{time_slot.label}"] = shift_info

    context = {
        "week_number": target_week.isocalendar()[1],
        "week_offset": week_offset,
        "weekdays_combined": weekdays_combined,
        "weekend_dates": [saturday_date.strftime("%Y-%m-%d")],
        "weekday_times": weekday_time_slots,
        "saturday_times": saturday_time_slots,
        "username": request.user.username,
        "today_date": today.strftime('%A, %d %B %Y'),
        "shifts": shifts,
        "shift_map": shift_map,
        "volunteer_limits": volunteer_limits,
        "all_users": User.objects.all() if request.user.is_staff else [],
        "workers_for_admin": workers_for_admin,
        "timestamp": datetime.now().timestamp(),
    }

    return render(request, "shifts/schedule.html", context)
