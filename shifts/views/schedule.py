from datetime import datetime, timedelta
from shifts.models import VolunteerLimit, ShiftAssignment, TimeSlot
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import logging
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.http import HttpResponse
import weasyprint
User = get_user_model()

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)
@login_required
def schedule_view(request, week_offset=0):
    logger.debug(f"Week Offset: {week_offset}")

    today = datetime.now()
    target_week = today + timedelta(weeks=int(week_offset))
    start_of_week = target_week - timedelta(days=target_week.weekday())

    shifts = []
    shift_map = {}

    weekdays_combined = [
        ((start_of_week + timedelta(days=i)).strftime("%A"),
         (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d"))
        for i in range(5)
    ]

    weekday_time_slots = TimeSlot.objects.filter(is_weekend=False)
    saturday_time_slots = TimeSlot.objects.filter(is_weekend=True)
    volunteer_limits = {obj.date.strftime("%Y-%m-%d"): obj.limit for obj in VolunteerLimit.objects.all()}

    # ✅ Admin should see ALL users (workers + volunteers)
    all_users_for_admin = User.objects.all() if request.user.is_staff else []

    def build_shift(date, date_str, time_slot):
        assignments = ShiftAssignment.objects.filter(date=date, time_slot=time_slot)
        workers = [a.user for a in assignments if a.role == "worker"]
        volunteers = [a.user for a in assignments if a.role == "volunteer"]

        shift_info = {
            "date": date_str,
            "time_slot": time_slot,
            "workers": workers,
            "volunteers": volunteers,
            "users": [u.username for u in volunteers],
            "max_slots": volunteer_limits.get(date_str, 2),
        }
        print("DEBUG shift_map type:", type(shift_map))
        print("DEBUG time_slot type:", type(time_slot))


        week_flag = "WE" if time_slot.is_weekend else "WD"
        shift_map[f"{date_str}|{time_slot.label}|{week_flag}"] = shift_info

        return shift_info

    for i in range(5):
        date = start_of_week + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        for time_slot in weekday_time_slots:
            shifts.append(build_shift(date, date_str, time_slot))

    saturday_date = start_of_week + timedelta(days=5)
    saturday_str = saturday_date.strftime("%Y-%m-%d")
    for time_slot in saturday_time_slots:
        shifts.append(build_shift(saturday_date, saturday_str, time_slot))

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
        "all_users": all_users_for_admin,  # ✅ replaced workers_for_admin
        "timestamp": datetime.now().timestamp(),
    }

    return render(request, "shifts/schedule.html", context)



def schedule_view_context(request, week_offset=0):
    # Copy all your schedule_view logic up to `context = {...}`
    # but instead of render(), just return `context`
    logger.debug(f"Week Offset: {week_offset}")

    today = datetime.now()
    target_week = today + timedelta(weeks=int(week_offset))
    start_of_week = target_week - timedelta(days=target_week.weekday())

    
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
    # Weekdays (Monday to Friday)
# Weekdays (Monday to Friday)
    for i in range(5):
        date = start_of_week + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        for time_slot in weekday_time_slots:
            assignments = ShiftAssignment.objects.filter(date=date, time_slot=time_slot)
            workers = [a.user for a in assignments if a.role == "worker"]
            volunteers = [a.user for a in assignments if a.role == "volunteer"]  # <-- keep as User objects

            shift_info = {
                "date": date_str,
                "time_slot": time_slot,
                "workers": workers,
                "volunteers": volunteers,  # <-- pass User objects
                "users": [u.username for u in volunteers],  # for JS if needed
                "max_slots": volunteer_limits.get(date_str, 2),
            }

            shifts.append(shift_info)
            shift_map[f"{date_str}|{time_slot.label}"] = shift_info

    # Saturday
    saturday_date = start_of_week + timedelta(days=5)
    saturday_str = saturday_date.strftime("%Y-%m-%d")
    for time_slot in saturday_time_slots:
        assignments = ShiftAssignment.objects.filter(date=saturday_date, time_slot=time_slot)
        workers = [a.user for a in assignments if a.role == "worker"]
        volunteers = [a.user for a in assignments if a.role == "volunteer"]  # <-- keep as User objects

        shift_info = {
            "date": saturday_str,
            "time_slot": time_slot,
            "workers": workers,
            "volunteers": volunteers,
            "users": [u.username for u in volunteers],  # for JS
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


    return context

@login_required
def my_bookings(request):
    today = timezone.now().date()
    filter_option = request.GET.get("filter", "upcoming")

    # Base queryset
    user_shifts = ShiftAssignment.objects.filter(user=request.user)

    # Apply filters
    if filter_option == "upcoming":
        user_shifts = user_shifts.filter(date__gte=today).order_by("date", "time_slot")
    elif filter_option == "past":
        user_shifts = user_shifts.filter(date__lt=today).order_by("-date", "-time_slot")
    else:  # "all"
        user_shifts = user_shifts.order_by("date", "time_slot")

    # Pull time slots from DB
    weekday_times = TimeSlot.objects.filter(is_weekend=False)
    saturday_times = TimeSlot.objects.filter(is_weekend=True)

    context = {
        "user_shifts": user_shifts,
        "weekday_times": weekday_times,
        "saturday_times": saturday_times,
    }
    return render(request, "shifts/my_bookings.html", context)

@login_required
def schedule_pdf_view(request, week_offset=0):
    # 1️⃣ Get all the schedule data (reuse helper)
    response_context = schedule_view_context(request, week_offset)

    # 2️⃣ Render HTML from template
    html_string = render_to_string('shifts/schedule_pdf.html', response_context)

    # 3️⃣ Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="vaktplan_uke_{response_context["week_number"]}.pdf"'

    weasyprint.HTML(string=html_string).write_pdf(response)
    return response
