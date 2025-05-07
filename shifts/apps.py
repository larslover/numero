from django.apps import AppConfig

class ShiftsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shifts"

    def ready(self):
        import shifts.templatetags.custom_filters  # 👈 Force Django to load it
        import shifts.signals  # 👈 add this line to activate signals
