# app/templatetags/media_filters.py
from django import template

register = template.Library()

@register.filter
def image_url_clean(value):
    value = str(value)  # Convert ImageFieldFile to string (URL path)
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return f"/media/{value}"
