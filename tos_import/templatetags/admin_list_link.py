import os
from django import template
import locale
from django.contrib.admin.views.main import PAGE_VAR

locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.simple_tag
def change_list_link(cl, i):
    return cl.get_query_string({PAGE_VAR: i})


@register.simple_tag
def previous_change_link(cl):
    result = '#'
    if cl.page_num > 0:
        result = cl.get_query_string({PAGE_VAR: cl.page_num-1})

    return result


@register.simple_tag
def next_change_link(cl):
    result = '#'
    if cl.page_num < cl.paginator.num_pages - 1:
        result = cl.get_query_string({PAGE_VAR: cl.page_num + 1})

    return result


@register.simple_tag
def first_change_link(cl):
    return cl.get_query_string({PAGE_VAR: 0})


@register.simple_tag
def last_change_link(cl):
    return cl.get_query_string({PAGE_VAR: cl.paginator.num_pages - 1})