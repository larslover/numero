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
    user_shifts = ShiftAssignment.objects.filter(user=request.user, date__gte=today).order_by("date", "time_slot")
    return render(request, "shifts/my_bookings.html", {"user_shifts": user_shifts})

logger = logging.getLogger(__name__)

# Pull time slots from DB
weekday_times = TimeSlot.objects.filter(is_weekend=False)
saturday_times = TimeSlot.objects.filter(is_weekend=True)
@login_required
def schedule_view(request, week_offset=0):
    logger.debug(f"Week Offset: {week_offset}")

    today = datetime.now()
    target_week = today + timedelta(weeks=int(week_offset))
    start_of_week = target_week - timedelta(days=target_week.weekday())

    shifts = []
    shift_map = {}

    weekdays_combined = [
        ((start_of_week + timedelta(days=i)).strftime("%A"), (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d"))
        for i in range(5)
    ]

    weekday_time_slots = TimeSlot.objects.filter(is_weekend=False)
    saturday_time_slots = TimeSlot.objects.filter(is_weekend=True)

    volunteer_limits = {
        obj.date.strftime("%Y-%m-%d"): obj.limit
        for obj in VolunteerLimit.objects.all()
    }

    # Prepare this outside the loop to prevent UnboundLocalError
    workers_for_admin = User.objects.filter(userprofile__role='worker') if request.user.is_staff else []

    # Loop for weekdays (Monday to Friday)
    for i in range(5):
        date = start_of_week + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        for time_slot in weekday_time_slots:
            assignments = ShiftAssignment.objects.filter(date=date, time_slot=time_slot)
            volunteers = [a.user for a in assignments if a.role == "volunteer"]
            workers = [a.user for a in assignments if a.role == "worker"]

            logger.debug(f"Assignments for {date_str} {time_slot.label}: {assignments}")
            logger.debug(f"Workers for {date_str} {time_slot.label}: {workers}")

            shift_info = {
                "date": date_str,
                "time_slot": time_slot,
                "users": volunteers,
                "workers": workers,
                "max_slots": volunteer_limits.get(date_str, 2),
            }

            shifts.append(shift_info)
            shift_map[f"{date_str}|{time_slot.label}"] = shift_info

    # Loop for Saturday
    saturday_date = start_of_week + timedelta(days=5)
    saturday_str = saturday_date.strftime("%Y-%m-%d")

    for time_slot in saturday_time_slots:
        assignments = ShiftAssignment.objects.filter(date=saturday_date, time_slot=time_slot)
        volunteers = [a.user.username for a in assignments if a.role == "volunteer"]
        workers = [a.user for a in assignments if a.role == "worker"]

        logger.debug(f"Assignments for {saturday_str} {time_slot.label}: {assignments}")
        logger.debug(f"Workers for {saturday_str} {time_slot.label}: {workers}")

        shift_info = {
            "date": saturday_str,
            "time_slot": time_slot,
            "users": volunteers,
            "workers": workers,
            "max_slots": volunteer_limits.get(saturday_str, 2),
        }

        shifts.append(shift_info)
        shift_map[f"{saturday_str}|{time_slot.label}"] = shift_info

    context = {
        "week_number": target_week.isocalendar()[1],
        "week_offset": week_offset,
        "weekdays_combined": weekdays_combined,
        "weekend_dates": [saturday_str],
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
