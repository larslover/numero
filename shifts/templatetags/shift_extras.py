from django import template

register = template.Library()

@register.simple_tag
def get_shift(shifts, date, time_slot):
    for shift in shifts:
        if shift["date"] == date and shift["time_slot"] == time_slot:
            # DO NOT convert anything – the data is already in string format
            return shift
    return None

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
