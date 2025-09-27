from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import TimeSlot, Shift
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


from django.contrib.auth.models import User  # Or wherever your User model is
from .models import ShiftAssignment  # Add this import

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import ShiftAssignment, TimeSlot
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import json
from .models import User, TimeSlot, Shift  # Adjust based on your actual models
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from shifts.models import ShiftAssignment  # Adjust based on your actual model location

@csrf_exempt
def remove_shift_assignment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body or '{}')  # Prevent empty body error
            user_id = data.get('user_id')
            date = data.get('date')
            time_slot_id = data.get('time_slot_id')

            if not (user_id and date and time_slot_id):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            deleted, _ = ShiftAssignment.objects.filter(
                user_id=user_id,
                date=date,
                time_slot_id=time_slot_id
            ).delete()

            if deleted == 0:
                return JsonResponse({'error': 'No matching shift found'}, status=404)

            return JsonResponse({'status': 'removed'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)

import json
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import TimeSlot, ShiftAssignment

def is_weekend(date_str):
    """Return True if the date string (YYYY-MM-DD) is Saturday/Sunday."""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception:
        return None
    return date_obj.weekday() >= 5  # 5=Saturday, 6=Sunday

def get_timeslot_safe(label=None, slot_id=None, date_str=None):
    """
    Return a TimeSlot object safely.
    Prefer lookup by id if provided. Otherwise require label + date_str to
    disambiguate weekday/weekend.
    """
    if slot_id:
        return TimeSlot.objects.filter(pk=slot_id).first()

    if not label or not date_str:
        return None

    weekend_flag = is_weekend(date_str)
    if weekend_flag is None:
        return None

    qs = TimeSlot.objects.filter(label=label, is_weekend=weekend_flag)
    return qs.first()  # returns None if no match


@csrf_exempt
def assign_shift(request):
    """
    Admin endpoint to assign a worker to a shift.
    Accepts JSON or form-encoded POST:
      - user_id
      - date (YYYY-MM-DD)
      - time_slot  (label)  OR time_slot_id (pk)
      - role (optional, defaults to 'worker')
    Responds with JSON: { ok: bool, status: 'success'|'error', message: '...' }
    """
    if request.method != "POST":
        return JsonResponse({"ok": False, "status": "error", "message": "Use POST"}, status=405)

    # parse body either as JSON or form POST
    data = {}
    content_type = request.META.get("CONTENT_TYPE", "")
    if "application/json" in content_type:
        try:
            data = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "status": "error", "message": "Invalid JSON"}, status=400)
    else:
        # form-encoded: use POST dict (works for standard form / fetch with form data)
        data = request.POST.dict() if hasattr(request, "POST") else {}

        # fallback: sometimes JS sends JSON but content-type missing; try to parse anyway
        if not data and request.body:
            try:
                data = json.loads(request.body.decode("utf-8") or "{}")
            except Exception:
                data = {}

    user_id = data.get("user_id") or data.get("user")
    date = data.get("date")
    time_slot_label = data.get("time_slot")
    time_slot_id = data.get("time_slot_id") or data.get("time_slot_pk")
    role = data.get("role", "worker")

    if not user_id or not date or (not time_slot_id and not time_slot_label):
        return JsonResponse({
            "ok": False,
            "status": "error",
            "message": "Missing required fields: user_id, date, and time_slot (label or id)."
        }, status=400)

    # fetch user
    user = User.objects.filter(pk=user_id).first()
    if not user:
        return JsonResponse({"ok": False, "status": "error", "message": "User not found."}, status=400)

    # fetch timeslot safely (handles same label for weekday/weekend)
    time_slot = get_timeslot_safe(label=time_slot_label, slot_id=time_slot_id, date_str=date)
    if not time_slot:
        return JsonResponse({
            "ok": False,
            "status": "error",
            "message": "TimeSlot not found for given date (did you pass the correct date format YYYY-MM-DD?)."
        }, status=400)

    # Prevent duplicate assignment in same role
    if ShiftAssignment.objects.filter(user=user, date=date, time_slot=time_slot, role=role).exists():
        return JsonResponse({
            "ok": False,
            "status": "error",
            "message": f"User is already assigned as {role} for this slot."
        }, status=400)

    # Optional: block cross-role double-booking (worker & volunteer same person same slot)
    if ShiftAssignment.objects.filter(user=user, date=date, time_slot=time_slot).exclude(role=role).exists():
        return JsonResponse({
            "ok": False,
            "status": "error",
            "message": "User already booked in the other role for this slot."
        }, status=400)

    # create assignment
    try:
        sa = ShiftAssignment.objects.create(user=user, date=date, time_slot=time_slot, role=role)
    except ValidationError as e:
        return JsonResponse({"ok": False, "status": "error", "message": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "status": "error", "message": f"Internal error: {e}"}, status=500)

    return JsonResponse({"ok": True, "status": "success", "message": "Shift assigned successfully", "shift_id": sa.id})

def get_time_slots(request):
    date_str = request.GET.get("date")
    try:
        print(f"Received date: {date_str}")  # Debugging: log the received date
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        is_weekend = date_obj.weekday() >= 5
        print(f"Is the date a weekend? {'Yes' if is_weekend else 'No'}")  # Debugging: log if the date is a weekend or weekday

        slots = TimeSlot.objects.filter(is_weekend=is_weekend)
        print(f"Filtered slots: {slots}")  # Debugging: log the filtered slots

        data = [{"id": slot.id, "label": slot.label} for slot in slots]
    except Exception as e:
        print(f"Error: {e}")  # Log the error if it occurs
        data = []

    return JsonResponse(data, safe=False)

def admin_check(user):
    return user.is_staff

@user_passes_test(admin_check)
def approve_users(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            messages.success(request, f"{user.username} has been approved!")
        except User.DoesNotExist:
            messages.error(request, "User not found!")
        return redirect('approve_users')

    pending_users = User.objects.filter(is_active=False)
    return render(request, "shifts/approve_users.html", {"pending_users": pending_users})

def admin_dashboard_view(request):
    return render(request, 'shifts/admin_dashboard.html')


@login_required
def assign_worker(request):
    if request.method == "POST":
        print("=== assign_worker POST START ===")
        print("Raw POST data:", request.POST)

        # Get parameters from POST
        date = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        user_id = request.POST.get('user_id')

        print(f"Received -> Date: {date}, Time Slot: {time_slot}, User ID: {user_id}")

        # Check for missing values
        if not all([date, time_slot, user_id]):
            print("⚠️ Missing one or more required fields.")
            return JsonResponse({"status": "error", "message": "Missing date, time_slot, or user_id"})

        try:
            # Modify this to query ShiftAssignment
            time_slot_obj = TimeSlot.objects.get(label=time_slot)  # Get the TimeSlot object by label
            print(f"✅ Found time slot: {time_slot_obj.label}")
        except TimeSlot.DoesNotExist:
            print(f"❌ No time slot found with label: {time_slot}")
            return JsonResponse({
                "status": "error",
                "message": f"No time slot found with label: {time_slot}"
            })

        try:
            shift_assignment = ShiftAssignment.objects.get(date=date, time_slot=time_slot_obj)
            print(f"✅ Found existing shift assignment for Date: {date}, Time Slot: {time_slot_obj.label}")
        except ShiftAssignment.DoesNotExist:
            print(f"❌ No shift assignment found for Date: {date}, Time Slot: {time_slot_obj.label}")
            return JsonResponse({
                "status": "error",
                "message": f"No ShiftAssignment found for date={date} and time_slot={time_slot}"
            })

        try:
            user = User.objects.get(id=user_id)
            print(f"✅ Found user with ID: {user_id} -> {user.username}")
        except User.DoesNotExist:
            print(f"❌ No user found with ID: {user_id}")
            return JsonResponse({
                "status": "error",
                "message": f"No User found with ID: {user_id}"
            })

        # Assign the worker to the shift
        shift_assignment.workers.add(user)
        shift_assignment.save()
        print(f"✅ Assigned {user.username} to shift on {date} at {time_slot_obj.label}")

        print("=== assign_worker POST END ===")
        return JsonResponse({"status": "success", "message": "Worker assigned successfully"})

    print("⚠️ assign_worker was accessed with non-POST method.")
    return JsonResponse({"status": "error", "message": "Invalid request method"})
