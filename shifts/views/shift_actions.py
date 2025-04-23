from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import json
from django.views.decorators.csrf import csrf_exempt
from ..models import ShiftAssignment, TimeSlot, VolunteerLimit  # Ensure VolunteerLimit is imported
from django.http import JsonResponse

from django.core.exceptions import ObjectDoesNotExist

def join_shift(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        date = data.get('date')
        time_slot_label = data.get('time_slot')  # e.g., "8:00 - 14:00"
        role = data.get('role')

        # Ensure required fields are present
        if not username or not date or not time_slot_label or not role:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        # Fetch TimeSlot based on time_slot_label
        try:
            time_slot = TimeSlot.objects.get(label=time_slot_label)
        except TimeSlot.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Time slot not found'})

        # Fetch the user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'})

        # Check if the user has already joined the shift
        existing_assignment = ShiftAssignment.objects.filter(
            user=user,
            date=date,
            time_slot=time_slot,
            role=role
        ).first()

        if existing_assignment:
            return JsonResponse({'status': 'error', 'message': 'Already joined the shift'})

        # Check if the volunteer limit has been reached
        try:
            volunteer_limit = VolunteerLimit.objects.get(date=date)
            current_volunteers = ShiftAssignment.objects.filter(date=date, role='volunteer').count()
            if current_volunteers >= volunteer_limit.limit:
                return JsonResponse({'status': 'error', 'message': 'Volunteer limit reached for this date'})
        except VolunteerLimit.DoesNotExist:
            pass  # No limit defined, proceed with the join

        # Create a new ShiftAssignment
        new_assignment = ShiftAssignment.objects.create(
            user=user,
            date=date,
            time_slot=time_slot,
            role=role
        )

        return JsonResponse({'status': 'success', 'created': True})

    except Exception as e:
        # Log the error and return a generic error response
        print(f"Error occurred: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal Server Error'}, status=500)

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
            username = data.get('username')
            date = data.get('date')
            time_slot_label = data.get('time_slot')
            role = data.get('role')

            if not username or not date or not time_slot_label or not role:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

            # Fetch TimeSlot based on time_slot_label
            try:
                time_slot = TimeSlot.objects.get(label=time_slot_label)
            except TimeSlot.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Time slot not found'})

            # Fetch the user
            try:
                user = User.objects.get(username=username)
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
