import locale
from django import template


locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.simple_tag
def stage(position_set, price):
    """
    Return current stage for position_set
    :param position_set: PositionSet
    :param price: float
    :return: str
    """
    # noinspection PyProtectedMember
    return position_set.get_stage(price=price).stage_name


@register.simple_tag
def status(position_set, position_equity):
    """
    Return current stage for position_set
    :param position_set: PositionSet
    :param position_equity: PositionEquity
    :return: str
    """
    # noinspection PyProtectedMember
    return position_set.current_status(
        new_price=position_equity.mark,
        old_price=position_equity.mark - position_equity.mark_change
    )


@register.simple_tag
def get_old_price(position_equity):
    """
    Return yesterday price of this position equity
    :param position_equity: PositionEquity
    :return: float
    """
    return position_equity.mark - position_equity.mark_change