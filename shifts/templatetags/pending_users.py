# shifts/templatetags/pending_users.py
from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.simple_tag
def count_pending_users():
    return User.objects.filter(is_active=False).count()
