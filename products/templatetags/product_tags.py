from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

from django.utils import timezone

register = template.Library()

@register.filter
def price_format(value):
    if value is None:
        return ""
    # Format with commas, then replace comma with a non-breaking space
    formatted_value = intcomma(int(value))
    return formatted_value.replace(",", " ") # Using non-breaking space

@register.filter
def added_label(created_at):
    if not created_at:
        return ""
    created = timezone.localtime(created_at)
    today = timezone.localtime(timezone.now())
    if created.date() == today.date():
        return "Bugun"
    if created.date() == (today - timezone.timedelta(days=1)).date():
        return "Kecha"
    return created.strftime("%d.%m.%Y")
