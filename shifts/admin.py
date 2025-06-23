from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import VolunteerLimit, ShiftAssignment, TimeSlot, UserProfile
from .forms import ShiftAssignmentForm
from django.contrib.admin import SimpleListFilter
from django.http import JsonResponse
import datetime

# Inline for UserProfile (unchanged)
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fields = ('role', 'bio', 'phone_number')

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else 1

    def has_add_permission(self, request, obj=None):
        if obj is None:
            return False
        return not UserProfile.objects.filter(user=obj).exists()

def get_time_slots(request):
    date_str = request.GET.get("date")
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        is_weekend = date_obj.weekday() >= 5
        slots = TimeSlot.objects.filter(is_weekend=is_weekend)
        data = [{"id": slot.id, "label": slot.label} for slot in slots]
    except Exception as e:
        data = []
    return JsonResponse(data, safe=False)


@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    form = ShiftAssignmentForm
    list_display = ("user", "date", "time_slot", "role")
    list_filter = ("date", "time_slot", "role")
    search_fields = ("user__username", "date", "time_slot")
    ordering = ("date", "time_slot")

    class Media:
        js = ("shifts/js/time_slot_dynamic.js",)


class TimeSlotWeekendFilter(SimpleListFilter):
    title = 'Weekend Filter'
    parameter_name = 'is_weekend'

    def lookups(self, request, model_admin):
        return (
            ('True', 'Weekend'),
            ('False', 'Weekday'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(is_weekend=True)
        if self.value() == 'False':
            return queryset.filter(is_weekend=False)
        return queryset


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("label", "is_weekend", "order")
    list_editable = ("is_weekend", "order")
    ordering = ("order",)
    list_filter = (TimeSlotWeekendFilter,)


@admin.register(VolunteerLimit)
class VolunteerLimitAdmin(admin.ModelAdmin):
    list_display = ("date", "limit")
    ordering = ("date",)
    search_fields = ("date",)
    list_filter = ("date",)


# Custom filter to filter users by role from UserProfile
class RoleFilter(SimpleListFilter):
    title = 'Rolle'  # Displayed title in admin sidebar
    parameter_name = 'role'

    def lookups(self, request, model_admin):
        return (
            ('worker', 'Ansatt'),
            ('volunteer', 'Frivillig'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'worker':
            return queryset.filter(userprofile__role='worker')
        elif self.value() == 'volunteer':
            return queryset.filter(userprofile__role='volunteer')
        return queryset

class UserAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline]

    list_display = ("username", "email", "is_active", "date_joined")
    list_filter = ("is_active", "date_joined", RoleFilter)
    actions = ["approve_users"]

    def approve_users(self, request, queryset):
        for user in queryset:
            if not user.is_active:
                user.is_active = True
                user.save()
    approve_users.short_description = "Approve selected users"

    def has_add_permission(self, request):
        # Return False to disable the "Add user" button for everyone
        return False

# Unregister default User admin and register the customized one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
