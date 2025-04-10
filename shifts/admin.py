from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import VolunteerLimit, ShiftAssignment,TimeSlot

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("label", "is_weekend", "order")
    list_editable = ("is_weekend", "order")
    ordering = ("order",)

# ✅ Custom admin for VolunteerLimit
@admin.register(VolunteerLimit)
class VolunteerLimitAdmin(admin.ModelAdmin):
    list_display = ("date", "limit")
    ordering = ("date",)
    search_fields = ("date",)
    list_filter = ("date",)

# ✅ Admin for ShiftAssignment
@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "time_slot", "role")
    list_filter = ("date", "time_slot", "role")
    search_fields = ("user__username", "date", "time_slot")
    ordering = ("date", "time_slot")

# ✅ Custom User admin with approval
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_active", "date_joined")
    list_filter = ("is_active", "date_joined")
    actions = ["approve_users"]

    def approve_users(self, request, queryset):
        for user in queryset:
            if not user.is_active:
                user.is_active = True
                user.save()
                send_mail(
                    "Your account has been approved",
                    "You can now log in to your account.",
                    "admin@yourdomain.com",
                    [user.email],
                    fail_silently=False,
                )

    approve_users.short_description = "Approve selected users"

# Replace default User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
