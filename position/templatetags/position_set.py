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
    return position_set.get_stage(price=price).stage_name


@register.simple_tag
def stage_box(position_set, price):
    """
    Return raw data that use for javascript split
    :param position_set: PositionSet
    :param price: float
    :return: str
    """
    # noinspection PyProtectedMember
    result = list()
    position_set = position_set
    """:type: PositionSet"""
    position_stages = position_set.positionstage_set.order_by('id').reverse()

    for position_stage in position_stages:
        tag = '{name},{exp},{price_a},{amount_a}'.format(
            name=position_stage.stage_name,
            exp=position_stage.stage_expression.format(
                current_price='PRICE',
                price_a=locale.currency(position_stage.price_a, grouping=True),
                price_b=locale.currency(position_stage.price_b, grouping=True)
            ),
            price_a=locale.currency(position_stage.price_a, grouping=True),
            amount_a=locale.currency(position_stage.amount_a, grouping=True),
        )

        if position_stage.price_b:
            tag += ',{price_b},{amount_b}'.format(
                price_b=locale.currency(position_stage.price_b, grouping=True),
                amount_b=locale.currency(position_stage.amount_b, grouping=True)
            )

        if position_stage.stage_name == position_set.get_stage(price=price).stage_name:
            tag += ',1'
        else:
            tag += ',0'

        result.append(tag)

    #return position_set.get_stage(price=price).stage_name
    return '|'.join(result)


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