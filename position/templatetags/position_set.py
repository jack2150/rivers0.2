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


@register.filter
def dict_item(items, key):
    """
    Return key item in dict
    :param items: dict
    :param key: str
    :return: str
    """
    return items[key]


# noinspection PyShadowingBuiltins
@register.filter
def split(text, id):
    """
    Split a text into list and get item in it
    :param text: str
    :return: str
    """
    return text.split(',')[id]


# noinspection PyShadowingNames
@register.filter
def explain(stage):
    """
    Stage
    :param stage: PositionStage
    :return: str
    """
    return stage.stage_expression.format(
        current_price='price',
        price_a=stage.price_a,
        price_b=stage.price_b
    )


@register.filter
def odd(item):
    """
    return true if item is odd
    :param item: int
    :return: int
    """
    return 1 if item % 2 == 0 else 0


@register.filter
def odd_jump1(x):
    """
    Return a odd jump key in for loop
    :param x: int
    :return: int
    """
    return x * 2 + 1


@register.filter
def odd_jump2(x):
    """
    Return a odd jump key in for loop
    :param x: int
    :return: int
    """
    return x * 2 + 2


@register.filter
def remove_underscore(x):
    """
    Remove underlying for str x
    :param x: str
    :return: str
    """
    return x.replace('_', ' ')


@register.filter
def get_close_pl(position_set):
    """
    Return last position instruments pl for position set
    :param position_set: PositionSet
    :return: float
    """
    position_instruments = position_set.positioninstrument_set\
        .order_by('position_summary__date').reverse()

    return float(
        position_instruments[0].pl_day + position_instruments[1].pl_open
    )

@register.filter
def last(instance):
    """
    Any model queryset and get last item in the list
    :param instance: model
    :return: model
    """
    return list(instance)[-1]


