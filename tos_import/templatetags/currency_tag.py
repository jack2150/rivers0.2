from django import template
import locale

locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.filter
def currency(value):
    """
    Format value into currency str
    :param value: float
    :return: str
    """
    try:
        result = locale.currency(value, grouping=True)
    except TypeError:
        result = locale.currency(0.0, grouping=True)

    return result
