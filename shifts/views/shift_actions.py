from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from datetime import datetime
import json

from ..models import ShiftAssignment, TimeSlot, VolunteerLimit


def is_weekend(date_str):
    """Return True if the date is Saturday or Sunday."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    return date_obj.weekday() >= 5  # 5 = Saturday, 6 = Sunday


def get_timeslot_safe(label, date_str):
    """Fetch a TimeSlot by label and weekend flag safely."""
    weekend_flag = is_weekend(date_str)
    try:
        return TimeSlot.objects.get(label=label, is_weekend=weekend_flag)
    except TimeSlot.DoesNotExist:
        return None
    except TimeSlot.MultipleObjectsReturned:
        # Fallback: pick the first one
        return TimeSlot.objects.filter(label=label, is_weekend=weekend_flag).first()

@csrf_exempt
def join_shift(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        print("=== join_shift called ===")
        print("Raw body:", request.body)

        data = json.loads(request.body)
        user_id = data.get('user_id')
        date = data.get('date')
        time_slot_label = data.get('time_slot')
        role = data.get('role')

        print(f"Parsed data -> user_id: {user_id}, date: {date}, time_slot: {time_slot_label}, role: {role}")

        if not user_id or not date or not time_slot_label or not role:
            print("⚠️ Missing required fields")
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

        user = User.objects.filter(id=user_id).first()
        if not user:
            print(f"❌ User not found for ID {user_id}")
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=400)
        print(f"✅ Found user: {user.username}")

        time_slot = get_timeslot_safe(time_slot_label, date)
        if not time_slot:
            print(f"❌ TimeSlot not found for label '{time_slot_label}' on date {date}")
            return JsonResponse({'status': 'error', 'message': 'Invalid time slot'}, status=400)
        print(f"✅ Found timeslot: {time_slot}")

        exists = ShiftAssignment.objects.filter(user=user, date=date, time_slot=time_slot, role=role).exists()
        print("Existing assignment?", exists)
        if exists:
            return JsonResponse({'status': 'error', 'message': 'User is already booked for this shift'}, status=400)

        sa = ShiftAssignment.objects.create(user=user, date=date, time_slot=time_slot, role=role)
        print(f"✅ Created ShiftAssignment: {sa.id}")

        return JsonResponse({'status': 'success', 'message': 'Shift joined successfully'}, status=200)

    except json.JSONDecodeError:
        print("❌ JSON decode error")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
    except Exception as e:
        print(f"❌ Exception: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@login_required
def cancel_shift(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method. Use POST.'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        date = data.get('date')
        time_slot_label = data.get('time_slot')
        role = data.get('role')

        if not user_id or not date or not time_slot_label or not role:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        user = User.objects.filter(id=user_id).first()
        if not user:
            return JsonResponse({'status': 'error', 'message': 'User not found'})

        time_slot = get_timeslot_safe(time_slot_label, date)
        if not time_slot:
            return JsonResponse({'status': 'error', 'message': 'Time slot not found'})

        shift_to_cancel = ShiftAssignment.objects.filter(user=user, date=date, time_slot=time_slot, role=role).first()
        if not shift_to_cancel:
            return JsonResponse({'status': 'error', 'message': 'No shift found to cancel'})

        shift_to_cancel.delete()
        return JsonResponse({'status': 'success', 'message': 'Shift canceled successfully'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Internal Server Error: ' + str(e)}, status=500)


@csrf_exempt
def save_shifts(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Invalid request method. Only POST is allowed."})

    try:
        data = json.loads(request.body)
        username = data.get('username')
        date = data.get('date')
        time_slot_label = data.get('time_slot')
        role = data.get('role', 'worker')

        if not username or not date or not time_slot_label:
            return JsonResponse({"success": False, "message": "Username, date, and time slot are required."})

        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({"success": False, "message": f"User '{username}' does not exist."})

        time_slot = get_timeslot_safe(time_slot_label, date)
        if not time_slot:
            return JsonResponse({"success": False, "message": f"Time slot '{time_slot_label}' does not exist."})

        if ShiftAssignment.objects.filter(user=user, date=date, time_slot=time_slot, role=role).exists():
            return JsonResponse({"success": False, "message": "Shift for this user already exists."})

        ShiftAssignment.objects.create(user=user, date=date, time_slot=time_slot, role=role)

        return JsonResponse({"success": True, "message": "Shift saved successfully."})

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


def get_saved_shifts(request):
    shifts = ShiftAssignment.objects.select_related("user", "time_slot").all()
    shift_data = [
        {
            "user": s.user.username,
            "date": s.date.strftime("%Y-%m-%d"),
            "time": s.time_slot.label if hasattr(s.time_slot, "label") else str(s.time_slot),
            "role": s.role
        }
        for s in shifts
    ]
    return JsonResponse({"shifts": shift_data})


@csrf_exempt
@login_required
def my_shifts_view(request):
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Invalid request method"})

    user = request.user
    shifts = ShiftAssignment.objects.filter(user=user).select_related("time_slot")
    shift_list = [
        {
            "date": s.date.strftime("%Y-%m-%d"),
            "time_slot": s.time_slot.label if hasattr(s.time_slot, "label") else str(s.time_slot)
        }
        for s in shifts
    ]
    return JsonResponse({"status": "ok", "shifts": shift_list})
