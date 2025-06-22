from django.contrib import admin
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .models import VolunteerLimit, ShiftAssignment, TimeSlot
from .forms import ShiftAssignmentForm
from django.contrib.admin import SimpleListFilter
# admin_views.py
from django.http import JsonResponse
from .models import TimeSlot
import datetime
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
   
    fields = ('role', 'bio', 'phone_number') 


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


# Custom filter for filtering by weekend/weekday
class TimeSlotWeekendFilter(SimpleListFilter):
    title = 'Weekend Filter'  # or use _('Weekend') for translations
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
    list_filter = (TimeSlotWeekendFilter,)  # Add the custom filter here

# ✅ Custom admin for VolunteerLimit
@admin.register(VolunteerLimit)
class VolunteerLimitAdmin(admin.ModelAdmin):
    list_display = ("date", "limit")
    ordering = ("date",)
    search_fields = ("date",)
    list_filter = ("date",)

# ✅ Custom User admin with approval
class UserAdmin(admin.ModelAdmin):
    inlines = [UserProfileInline]  # This is still fine

    list_display = ("username", "email", "is_active", "date_joined")
    list_filter = ("is_active", "date_joined")
    actions = ["approve_users"]

    def approve_users(self, request, queryset):
        for user in queryset:
            if not user.is_active:
                user.is_active = True
                user.save()

    approve_users.short_description = "Approve selected users"


# Replace default User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
