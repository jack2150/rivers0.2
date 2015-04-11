import locale
from django import template

locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.filter()
def group_int(value):
    return locale.format('%d', value, True)
