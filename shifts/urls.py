# shifts/urls.py
from django.urls import path
from .views_auth import custom_login, signup, custom_logout
from .views_admin import approve_users, admin_dashboard_view, assign_worker
from .views.schedule import schedule_view ,my_bookings # Import directly from the correct file
from django.views.generic import RedirectView
import shifts.views_admin as views_admin
from django.urls import path, re_path
from .views.shift_actions import (
    join_shift, cancel_shift,
    save_shifts, get_saved_shifts, my_shifts_view
)
from .views.schedule import schedule_view
from django.contrib.auth import views as auth_views
from .views_admin import get_time_slots,assign_shift
from django.urls import re_path
urlpatterns = [
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path("my-bookings/", my_bookings, name="my_bookings"),
    path('api/remove/', views_admin.remove_shift_assignment, name='remove_shift'),
    path('', RedirectView.as_view(url='/schedule/', permanent=False)),
    path("get-time-slots/", get_time_slots, name="get_time_slots"),
    path('assign_worker/', assign_worker, name='assign_worker'),
    path("logout/", custom_logout, name="logout"),
    path('schedule/', schedule_view, name='schedule_view'),
    path('api/assign/',assign_shift, name='assign_shift'),


# Modify the URL pattern to accept negative numbers
    re_path(r'^schedule/(?P<week_offset>-?\d+)/$', schedule_view, name='schedule_week'),


  
    path("api/save_shifts/", save_shifts, name="save_shifts"),
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
