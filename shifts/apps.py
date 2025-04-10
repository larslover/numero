from django.apps import AppConfig

class ShiftsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shifts"

    def ready(self):
        import shifts.templatetags.custom_filters  # 👈 Force Django to load it
