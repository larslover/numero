from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin import SimpleListFilter
from django.http import JsonResponse
import datetime

from .models import Shift, ShiftAssignment, TimeSlot, VolunteerLimit, UserProfile
from .forms import ShiftAssignmentForm

# -----------------------
# Admin Site Header
# -----------------------
admin.site.site_header = "Vaktplan Admin"
admin.site.site_title = "Vaktplan"
admin.site.index_title = "Administrasjon"

# -----------------------
# UserProfile Inline
# -----------------------
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profil"
    fields = ('role', 'bio', 'phone_number')

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else 1

    def has_add_permission(self, request, obj=None):
        if obj is None:
            return False
        return not UserProfile.objects.filter(user=obj).exists()

# -----------------------
# Shift Admin
# -----------------------
@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('date', 'time_slot')
    ordering = ('date', 'time_slot')
    # verbose_name_plural is read from model Meta, no need to set here

# -----------------------
# ShiftAssignment Admin
# -----------------------
@admin.register(ShiftAssignment)
class ShiftAssignmentAdmin(admin.ModelAdmin):
    form = ShiftAssignmentForm
    list_display = ("user", "date", "time_slot", "role")
    list_filter = ("date", "time_slot", "role")
    search_fields = ("user__username", "date", "time_slot")
    ordering = ("date", "time_slot")

    class Media:
        js = ("shifts/js/time_slot_dynamic.js",)

# -----------------------
# TimeSlot Admin
# -----------------------
class TimeSlotWeekendFilter(SimpleListFilter):
    title = 'Helg / Ukedag'
    parameter_name = 'is_weekend'

    def lookups(self, request, model_admin):
        return (
            ('True', 'Helg'),
            ('False', 'Ukedag'),
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

# -----------------------
# VolunteerLimit Admin
# -----------------------
@admin.register(VolunteerLimit)
class VolunteerLimitAdmin(admin.ModelAdmin):
    list_display = ("date", "limit")
    ordering = ("date",)
    search_fields = ("date",)
    list_filter = ("date",)

# -----------------------
# Role Filter for Users
# -----------------------
class RoleFilter(SimpleListFilter):
    title = 'Rolle'
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

# -----------------------
# Custom User Admin
# -----------------------
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
    approve_users.short_description = "Godkjenn valgte brukere"

    def has_add_permission(self, request):
        return False

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
