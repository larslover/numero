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


@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
@api_view(['POST'])

def assign_shift(request):
    print(f"Received data: {request.data}")
    user_id = request.data.get('user_id')
    date = request.data.get('date')
    time_slot_label = request.data.get('time_slot')

    try:
        user = User.objects.get(id=user_id)
        time_slot = TimeSlot.objects.get(label=time_slot_label)
    except (User.DoesNotExist, TimeSlot.DoesNotExist):
        return Response({"error": "User or TimeSlot not found"}, status=400)

    shift_assignment = ShiftAssignment.objects.create(
        user=user,
        date=date,
        time_slot=time_slot,
        role='worker'
    )

    return Response({"status": "success", "message": "Shift assigned successfully"})


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
            # ✅ No email sent
            messages.success(request, f"{user.username} har blitt godkjent!")
        except User.DoesNotExist:
            messages.error(request, "Bruker ble ikke funnet.")
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
