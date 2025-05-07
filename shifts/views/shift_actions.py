from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import json
from ..models import ShiftAssignment, TimeSlot, VolunteerLimit # Ensure VolunteerLimit is imported
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
import json  # Make sure you import json if you haven't already


@csrf_exempt
def join_shift(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            user_id = data.get('user_id')
            date = data.get('date')
            time_slot_label = data.get('time_slot')
            role = data.get('role')

            # Check that all required fields are provided
            if not user_id or not date or not time_slot_label or not role:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            # Ensure that the user exists
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'}, status=400)

            # Ensure that the time slot exists
            try:
                time_slot = TimeSlot.objects.get(label=time_slot_label)
            except TimeSlot.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid time slot'}, status=400)

            # Check if the user is already assigned to this shift
            existing_shift = ShiftAssignment.objects.filter(
                user=user,
                date=date,
                time_slot=time_slot,
                role=role
            ).exists()

            if existing_shift:
                return JsonResponse({'status': 'error', 'message': 'User is already booked for this shift'}, status=400)

            # Create the ShiftAssignment
            shift_assignment = ShiftAssignment.objects.create(
                user=user,
                date=date,
                time_slot=time_slot,
                role=role
            )

            return JsonResponse({'status': 'success', 'message': 'Shift joined successfully'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required
def cancel_shift(request):
    print("Path received:", request.path)

    if request.method == "POST":
        try:
            # Ensure that the request body is not empty
            if not request.body:
                return JsonResponse({'status': 'error', 'message': 'Request body is empty'})

            # Parse the JSON data
            data = json.loads(request.body)
            
            # Check if all required fields are present
            user_id = data.get('user_id')
            date = data.get('date')
            time_slot_label = data.get('time_slot')
            role = data.get('role')

            if not user_id or not date or not time_slot_label or not role:
              return JsonResponse({'status': 'error', 'message': 'Missing required fields'})


            # Fetch TimeSlot based on time_slot_label
            try:
                time_slot = TimeSlot.objects.get(label=time_slot_label)
            except TimeSlot.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Time slot not found'})

            # Fetch the user
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'User not found'})


            # Check if the user is assigned to the shift
            shift_to_cancel = ShiftAssignment.objects.filter(
                user=user,
                date=date,
                time_slot=time_slot,
                role=role
            ).first()

            if not shift_to_cancel:
                return JsonResponse({'status': 'error', 'message': 'No shift found to cancel'})

            # Delete the shift assignment
            shift_to_cancel.delete()

            return JsonResponse({'status': 'success', 'message': 'Shift canceled successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
        except Exception as e:
            # Log the error and return a generic error response
            print(f"Error occurred: {e}")
            return JsonResponse({'status': 'error', 'message': 'Internal Server Error'}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid HTTP method. Use POST.'}, status=405)







def save_shifts(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            username = data.get('username')
            date = data.get('date')
            time_slot_label = data.get('time_slot')  # e.g. "12:00 PM - 1:00 PM"
            role = data.get('role', 'worker')  # Default to 'worker' if not specified

            if not username or not date or not time_slot_label:
                return JsonResponse({
                    "success": False,
                    "message": "Username, date, and time slot are required."
                })

            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": f"User with username '{username}' does not exist."
                })

            try:
                time_slot = TimeSlot.objects.get(label=time_slot_label)
            except TimeSlot.DoesNotExist:
                return JsonResponse({
                    "success": False,
                    "message": f"Time slot '{time_slot_label}' does not exist."
                })

            # Check for existing shift
            if ShiftAssignment.objects.filter(user=user, date=date, time_slot=time_slot, role=role).exists():
                return JsonResponse({
                    "success": False,
                    "message": "Shift for this user already exists."
                })

            # Create and save the shift
            ShiftAssignment.objects.create(
                user=user,
                date=date,
                time_slot=time_slot.label,
                role=role
            )

            return JsonResponse({"success": True, "message": "Shift saved successfully."})

        except Exception as e:
            print(f"Error saving shift: {e}")
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
