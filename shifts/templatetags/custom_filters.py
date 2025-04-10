from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns the value of the dictionary for the given key."""
    try:
        return dictionary[key]
    except KeyError:
        return None
