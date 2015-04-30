from importlib import import_module
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from pandas.tseries.offsets import Day, Hour, Minute
from data.holidays import is_holiday
from data.models import Stock, get_price, get_option
from data.offdays import is_offdays
from position.models import *
from tos_import.statement.statement_position.models import *
from pandas import bdate_range


# noinspection PyShadowingNames
def spread_view(request, date=''):
    """
    Spread view: detail stage management for all positions
    :param request: request
    :param date: str 2015-01-31
    :return: render
    """
    template = 'position/spread/index.html'

    position_summary = None
    position_instruments = None
    position_futures = None
    position_forexs = None
    previous_item = None
    next_item = None

    if date:
        position_summary = PositionSummary.objects.filter(date=date)

        if position_summary.exists():
            position_summary = position_summary.first()

    else:
        if PositionSummary.objects.exists():
            position_summary = PositionSummary.objects.latest('date')
            date = position_summary.date

    if position_summary:
        position_instruments = PositionInstrument.objects.filter(
            position_summary=position_summary
        )
        position_futures = PositionFuture.objects.filter(
            position_summary=position_summary
        )
        position_forexs = PositionForex.objects.filter(
            position_summary=position_summary
        )

        # page navigator
        previous_obj = PositionSummary.objects.filter(date__lt=date).order_by('date').reverse()
        if previous_obj.exists():
            previous_item = previous_obj[0].date.strftime('%Y-%m-%d')

        next_obj = PositionSummary.objects.filter(date__gt=date).order_by('date')
        if next_obj.exists():
            next_item = next_obj[0].date.strftime('%Y-%m-%d')

    parameters = dict(
        date=date,
        position_instruments=position_instruments,
        position_futures=position_futures,
        position_forexs=position_forexs,
        previous=previous_item,
        next=next_item
    )

    return render(request, template, parameters)


# noinspection PyShadowingNames,PyShadowingBuiltins
def next_bday(date):
    """
    Return next bday which it is not holidays or offdays
    :param date: str
    :return: datetime
    """
    add_day = 1
    next_bday = datetime.strptime(date, '%Y-%m-%d') + BDay(add_day)
    # check it is not holiday
    while is_holiday(date=next_bday.strftime('%Y-%m-%d')) \
            or is_offdays(date=next_bday.strftime('%m/%d/%y')):
        add_day += 1
        next_bday = datetime.strptime(date, '%Y-%m-%d') + BDay(add_day)

    return next_bday.strftime('%Y-%m-%d')


# noinspection PyShadowingBuiltins
def position_add_opinion_view(request, id, date, direction, decision):
    """
    Ajax add position opinion using latest date + 1 Bday
    :param request: request
    :param date: str
    :param id: int
    :param direction: str
    :param decision: str
    :return: HttpResponse
    """
    position_set = PositionSet.objects.get(id=id)

    # set position opinion
    position_opinion = PositionOpinion()
    position_opinion.position_set = position_set
    position_opinion.direction = direction.upper()
    position_opinion.decision = decision.upper()

    # set date
    position_opinion.date = next_bday(date)

    position_opinion.save()

    return HttpResponse("success %d" % position_opinion.id, content_type="text/plain")


def update_opinion_results(request):
    """
    How to use:
    update_opinion_results()
    """
    # set open and close opinion
    position_sets = PositionSet.objects.all()
    for position_set in position_sets:

        filled_orders = position_set.filledorder_set.all()
        if filled_orders.filter(pos_effect='TO OPEN').exists():
            date = filled_orders.filter(pos_effect='TO OPEN').first().trade_summary.date

            if not position_set.positionopinion_set.filter(date=date).exists():
                position_opinion = PositionOpinion()
                position_opinion.position_set = position_set
                position_opinion.decision = 'OPEN'
                position_opinion.analysis = 'SIMPLE'
                position_opinion.date = date
                position_opinion.save()

        if filled_orders.filter(pos_effect='TO CLOSE').exists():
            date = filled_orders.filter(pos_effect='TO CLOSE').first().trade_summary.date

            if not position_set.positionopinion_set.filter(date=date).exists():
                position_opinion = PositionOpinion()
                position_opinion.position_set = position_set
                position_opinion.decision = 'CLOSE'
                position_opinion.analysis = 'SIMPLE'
                position_opinion.date = date
                position_opinion.save()

    # get all position opinions
    position_opinions = PositionOpinion.objects.exclude(
        Q(direction__isnull=True) & Q(decision__isnull=True)
    ).exclude(
        Q(decision='OPEN') | Q(decision='CLOSE')
    ).order_by('date')

    if position_opinions.exists():
        for position_opinion in position_opinions:
            try:
                position_instruments = position_opinion.position_set.positioninstrument_set.filter(
                    position_summary__date__lte=position_opinion.date
                ).order_by('position_summary__date').reverse()[:2]

                yesterday = position_instruments[1].position_summary.date

                stock0 = get_price(
                    symbol=position_opinion.position_set.underlying.symbol,
                    date=yesterday,
                    source='google'
                )

                stock1 = get_price(
                    symbol=position_opinion.position_set.underlying.symbol,
                    date=position_opinion.date,
                    source='google'
                )

                # start compare
                if stock1.close > stock0.close:
                    # is bull
                    if position_opinion.direction == 'BULL':
                        position_opinion.direction_result = True
                    else:
                        position_opinion.direction_result = False
                elif stock1.close < stock0.close:
                    # is bear
                    if position_opinion.direction == 'BEAR':
                        position_opinion.direction_result = True
                    else:
                        position_opinion.direction_result = False

                # for pl open now
                if position_instruments[0].pl_open > position_instruments[1].pl_open:
                    if position_opinion.decision in ('HOLD', 'CLOSE'):
                        position_opinion.decision_result = True
                    else:
                        position_opinion.decision_result = False
                elif position_instruments[0].pl_open < position_instruments[1].pl_open:
                    if position_opinion.decision in ('HOLD', 'CLOSE'):
                        position_opinion.decision_result = False
                    else:
                        position_opinion.decision_result = True

                position_opinion.save()
            except AttributeError:
                continue

    return redirect(reverse('admin:position_positionopinion_changelist'))


# noinspection PyShadowingBuiltins
def profiler_view(request, id=0, date=None):
    """
    New profiler view for all different spread
    :param request: request
    :param id: int
    :param date: str
    :return: render
    """
    template = 'position/profiler/index.html'

    position_set = PositionSet.objects.get(id=id)

    profiler_module = import_module('position.classes.profiler.%s' % position_set.name.lower())
    profiler_class = getattr(
        profiler_module,
        'Profiler%s' % ''.join(map(lambda x: x.capitalize(), position_set.spread.split('_')))
    )

    profiler = profiler_class(position_set, date)

    # page navigator
    paginator = dict(
        first=None,
        previous=None,
        next=None,
        last=None
    )

    dates = [p[0] for p in
             position_set.positioninstrument_set.all().values_list('position_summary__date')]
    index = dates.index(profiler.date)

    if index != 0:
        paginator['first'] = dates[0]
        paginator['previous'] = dates[index-1]

    if len(dates) != index + 1:
        paginator['next'] = dates[index + 1]
        paginator['last'] = dates[-1]

    parameters = dict(
        position_set=position_set,
        position_info=profiler.create_position_info(),
        position_dates=profiler.create_position_dates,
        position_stages=position_set.positionstage_set.all(),
        position_instruments=profiler.position_instruments,
        position_opinions=profiler.create_position_opinions(),
        position_stocks=profiler.create_position_stocks(),

        historical_positions=profiler.create_historical_positions(),
        opinion_button=profiler.create_opinion_button(),

        paginator=paginator,
    )

    return render(request, template, parameters)