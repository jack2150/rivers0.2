from django import template

register = template.Library()


@register.filter()
def title_split(value):
    return ' '.join(map(lambda x: x.capitalize(), value.split('_')))
