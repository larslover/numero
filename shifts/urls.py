from django.urls import path, re_path
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

from .views_auth import custom_login, signup, custom_logout
from .views_admin import approve_users, admin_dashboard_view, assign_worker, get_time_slots, assign_shift
from .views.schedule import schedule_view, my_bookings, schedule_pdf_view,save_daily_comment
from .views.shift_actions import join_shift, cancel_shift, save_shifts, get_saved_shifts, my_shifts_view
import shifts.views_admin as views_admin

urlpatterns = [
    # Allow negative week_offset for PDF download
    re_path(r'^schedule/pdf/(?P<week_offset>-?\d+)/$', schedule_pdf_view, name='schedule_pdf'),
    path('save-daily-comment/', save_daily_comment, name='save_daily_comment'),

    # Password reset routes
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

    # User views
    path("my-bookings/", my_bookings, name="my_bookings"),
    path("logout/", custom_logout, name="logout"),
    path("signup/", signup, name="signup"),
    path("login/", custom_login, name="login"),

    # Schedule views
    re_path(r'^schedule/(?P<week_offset>-?\d+)/$', schedule_view, name='schedule_week'),  # negative week_offset allowed
    path('schedule/', schedule_view, name='schedule_view'),

    # Admin / API
    path('api/remove/', views_admin.remove_shift_assignment, name='remove_shift'),
    path("get-time-slots/", get_time_slots, name="get_time_slots"),
    path('assign_worker/', assign_worker, name='assign_worker'),
    path('api/assign/', assign_shift, name='assign_shift'),

    path("api/save_shifts/", save_shifts, name="save_shifts"),
    path("api/my_shifts/", my_shifts_view, name="my_shifts"),
    path("api/join/", join_shift, name="join_shift"),
    path("api/cancel/", cancel_shift, name="cancel_shift"),
    path("save_shifts/", save_shifts, name="save_shifts"),
    path("get_saved_shifts/", get_saved_shifts, name="get_saved_shifts"),

    # Admin routes
    path("admin/approve-users/", approve_users, name="approve_users"),
    path("dashboard/", admin_dashboard_view, name="dashboard"),

    # Redirect default
    path('', RedirectView.as_view(url='/schedule/', permanent=False)),
]
