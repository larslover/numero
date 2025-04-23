# shifts/urls.py
from django.urls import path
from .views_auth import custom_login, signup, custom_logout
from .views_admin import approve_users, admin_dashboard_view, assign_worker
from .views.schedule import schedule_view
from .views.shift_actions import (
    join_shift, cancel_shift,
    save_shifts, get_saved_shifts, my_shifts_view
)

urlpatterns = [
    path("assign_worker/", assign_worker, name="assign_worker"),
    path("logout/", custom_logout, name="logout"),
    path("schedule/", schedule_view, name="schedule"),
    path("schedule/<slug:week_offset>/", schedule_view, name="schedule_week"),
    path("api/my_shifts/", my_shifts_view, name="my_shifts"),
    path("api/join/", join_shift, name="join_shift"),
    path("api/cancel/", cancel_shift, name="cancel_shift"),
    path("save_shifts/", save_shifts, name="save_shifts"),
    path("get_saved_shifts/", get_saved_shifts, name="get_saved_shifts"),
    # Admin routes
    path("admin/approve-users/", approve_users, name="approve_users"),
    path("dashboard/", admin_dashboard_view, name="dashboard"),
    # Auth routes
    path("signup/", signup, name="signup"),
    path("login/", custom_login, name="login"),
]
