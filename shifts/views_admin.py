# shifts/views_admin.py
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import render

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


def assign_worker(request):
    return render(request, "shifts/assign_worker.html")
