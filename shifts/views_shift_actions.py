from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import json
from .models import TimeSlot
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ShiftAssignment  # or wherever your model is



@csrf_exempt
@login_required
def join_shift(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            date = data.get("date")
            time_slot_label = data.get("time_slot")
            time_slot = TimeSlot.objects.get(label=time_slot_label)
            role = data.get("role")

            user = User.objects.get(username=username)

            shift, created = ShiftAssignment.objects.get_or_create(
                user=user,
                date=date,
                time_slot=time_slot,
                role=role
            )

            print(f"ShiftAssignment {'created' if created else 'already existed'} for {user.username} on {date} at {time_slot} as {role}")

            # 🔁 NEW PART: Include shift users
            users_in_shift = ShiftAssignment.objects.filter(date=date, time_slot=time_slot)
            usernames = [s.user.username for s in users_in_shift]

            return JsonResponse({
                "status": "success",
                "created": created,
                "shift": {
                    "date": date,
                    "time_slot": time_slot.label,
                    "users": usernames
                }
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "invalid request"})
@csrf_exempt  # TODO: remove this and handle CSRF properly later
@login_required
def cancel_shift(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            date = data.get("date")
            time_slot_label = data.get("time_slot")

            user = User.objects.get(username=username)
            time_slot = TimeSlot.objects.get(label=time_slot_label)

            deleted, _ = ShiftAssignment.objects.filter(
                user=user,
                date=date,
                time_slot=time_slot
            ).delete()

            return JsonResponse({"status": "deleted", "count": deleted})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    else:
        return JsonResponse({"status": "invalid request"})

@login_required
def schedule_api(request):
    shifts = ShiftAssignment.objects.select_related("user").all()  # 'user' instead of 'volunteer'
    
    volunteers = {
        f"{shift.date}-{shift.time_slot}": shift.user.username
        for shift in shifts if shift.user
    }

    shift_list = [
        {"day": shift.date.strftime("%Y-%m-%d"), "time_slot": shift.time_slot, "volunteer": shift.user.username}
        for shift in shifts if shift.user
    ]

    return JsonResponse({"shifts": shift_list, "volunteers": volunteers})



@login_required


@csrf_exempt
def save_shifts(request):
    if request.method == "POST":
        try:
            # Get the data from the frontend
            data = json.loads(request.body)
            username = data.get('username')

            if not username:
                return JsonResponse({"success": False, "message": "Username is required."})

            # Get the user based on the provided username
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({"success": False, "message": f"User with username '{username}' does not exist."})

            # Check if the shift already exists
            existing_shift = ShiftAssignment.objects.filter(
                user=user,
                date='2025-04-07',  # Adjust as per your requirements
                time_slot='12:00 PM - 1:00 PM',
                role='worker'
            ).exists()

            if existing_shift:
                return JsonResponse({"success": False, "message": "Shift for this user already exists."})

            # Create and save the shift
            shift = ShiftAssignment.objects.create(
                user=user,
                date='2025-04-07',  # Adjust as per your requirements
                time_slot='12:00 PM - 1:00 PM',  # Adjust as per your requirements
                role='worker'
            )
            shift.save()  # Ensure save() is called
            
            # Return success response
            return JsonResponse({"success": True, "message": "Shift saved successfully."})
        
        except Exception as e:
            # Log the error and return a response
            print(f"Error saving shift: {e}")  # Replace with proper logging if needed
            return JsonResponse({"success": False, "message": str(e)})

    return JsonResponse({"success": False, "message": "Invalid request method. Only POST is allowed."})

def get_saved_shifts(request):
  shifts = ShiftAssignment.objects.select_related("user").all()

  shift_data = [
      {
          "user": shift.user.username,
          "date": shift.date.strftime("%Y-%m-%d"),
          "time": shift.time_slot,
          "role": shift.role
      }
      for shift in shifts
  ]

  return JsonResponse({"shifts": shift_data})


@csrf_exempt
@login_required
def my_shifts_view(request):
    if request.method == "GET":
        user = request.user
        shifts = ShiftAssignment.objects.filter(user=user)
        shift_list = [
            {
                "date": s.date.strftime("%Y-%m-%d"),
                "time_slot": s.time_slot.label if hasattr(s.time_slot, "label") else str(s.time_slot)
            }
            for s in shifts
        ]
        return JsonResponse({"status": "ok", "shifts": shift_list})
    return JsonResponse({"status": "error", "message": "Invalid request method"})
