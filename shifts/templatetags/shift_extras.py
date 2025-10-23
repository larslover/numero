from django import template

register = template.Library()

@register.simple_tag
def get_shift(shifts, date, time_slot):
    for shift in shifts:
        if shift["date"] == date and shift["time_slot"] == time_slot:
            # DO NOT convert anything – the data is already in string format
            return shift
    return None
# shift_extras.py (add this at the bottom)

@register.filter
def dict_get(d, key):
    """Safely get a value from a dictionary."""
    if d is None:
        return None
    return d.get(key)

# In shift_extras.py
@register.filter
def translate_weekday(value):
    return {
        'Monday': 'Mandag',
        'Tuesday': 'Tirsdag',
        'Wednesday': 'Onsdag',
        'Thursday': 'Torsdag',
        'Friday': 'Fredag',
        'Saturday': 'Lørdag',
        'Sunday': 'Søndag',
    }.get(value, value)
