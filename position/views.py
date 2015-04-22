from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect
from pandas.tseries.offsets import Day, Hour, Minute
from data.holidays import is_holiday
from data.models import Stock, get_price
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


def update_opinion_results(reqeust):
    """
    How to use:
    update_opinion_results()
    """
    # get all position opinions
    position_opinions = PositionOpinion.objects.exclude(
        Q(direction__isnull=True) & Q(direction__isnull=True)
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


# noinspection PyShadowingNames,PyShadowingBuiltins
def profiler_view(request, id=0, date=''):
    """
    Profiler view for a single position_set
    :param request: request
    :param id: int
    :return: render
    """
    template = 'position/profiler/index.html'

    # get position set and position stages
    position_set = PositionSet.objects.get(id=id)
    position_stages = position_set.positionstage_set.all()

    # display variables
    position_prices = dict()
    position_stocks = list()
    position_stage_movers = list()
    historical_position_sets = None

    # foreign keys
    if date:
        filled_orders = position_set.filledorder_set\
            .filter(trade_summary__date__lte=date).order_by('trade_summary__date')
        position_instruments = position_set.positioninstrument_set \
            .filter(position_summary__date__lte=date).order_by('position_summary__date')
    else:
        filled_orders = position_set.filledorder_set\
            .order_by('trade_summary__date').all()
        position_instruments = position_set.positioninstrument_set\
            .order_by('position_summary__date').all()

        date = position_instruments.last().position_summary.date.strftime('%Y-%m-%d')

    # position opinion section
    try:
        # opinion saved
        bday = next_bday(date)
        position_opinion = position_set.positionopinion_set\
            .filter(date__lte=bday).order_by('date').last()

        if bday == position_opinion.date.strftime('%Y-%m-%d'):
            position_opinion = dict(
                object=position_opinion,
                saved=True,
            )
        else:
            position_opinion = dict(saved=False)
    except AttributeError:
        position_opinion = dict(saved=False)

    # position opinions
    position_opinions = position_set.positionopinion_set.filter(
        date__lte=date
    ).order_by('date')

    #direction_cumsum = cumsum(position_opinions.values_list('direction_result'))
    bull = dict(count=0, count_pct=0.0, correct=0, correct_pct=0.0, wrong=0, wrong_pct=0.0)
    bear = dict(count=0, count_pct=0.0, correct=0, correct_pct=0.0, wrong=0, wrong_pct=0.0)
    for count, opinion in enumerate(position_opinions, start=1):
        if opinion.direction == 'BULL':
            bull['count'] += 1
            if opinion.direction_result:
                bull['correct'] += 1
            else:
                bull['wrong'] += 1
            bull['count_pct'] = round(bull['count'] / float(count) * 100, 2)
            bull['correct_pct'] = round(bull['correct'] / float(bull['count']) * 100, 2)
            bull['wrong_pct'] = round(bull['wrong'] / float(bull['count']) * 100, 2)

        elif opinion.direction == 'BEAR':
            bear['count'] += 1
            if opinion.direction_result:
                bear['correct'] += 1
            else:
                bear['wrong'] += 1
            bear['count_pct'] = round(bear['count'] / float(count) * 100, 2)
            bear['correct_pct'] = round(bear['correct'] / float(bear['count']) * 100, 2)
            bear['wrong_pct'] = round(bear['wrong'] / float(bear['count']) * 100, 2)

        # assign dict
        opinion.bull = bull.copy()
        opinion.bear = bear.copy()

    # calculate days
    start_date = position_instruments.first().position_summary.date
    stop_date = position_instruments.last().position_summary.date

    # get dates
    dte = 0
    expire_date = ''
    if not any([x in position_set.spread for x in ('CALENDAR', 'DIAGONAL')]):
        position_options = position_instruments.last().positionoption_set

        if position_options.exists():
            dte = position_instruments.last().positionoption_set.last().days + 1
            dte = dte if dte > 0 else 0  # reset if already expired

            expire_date = datetime.strptime((stop_date + Day(dte)).strftime('%Y-%m-%d'), '%Y-%m-%d').date()

    if stop_date != start_date:
        pass_bdays = len(bdate_range(start=start_date, end=stop_date))
        pass_days = (stop_date - start_date).days
    else:
        pass_bdays = len(bdate_range(start=start_date, end=datetime.today()))
        pass_days = (datetime.today().date() - start_date).days

    position_dates = dict(
        pass_bdays=pass_bdays,
        pass_days=pass_days,
        start_date=start_date,
        stop_date=stop_date,
        dte=dte,
        expire_date=expire_date,
    )

    if position_set.underlying:
        if position_set.name == 'EQUITY':
            # get stocks data
            stocks = Stock.objects.filter(
                Q(symbol=position_set.underlying.symbol) &
                #Q(date__gte=start_date - BDay(1)) &
                #Q(date__lte=stop_date) &
                Q(date__in=[i.position_summary.date for i in position_instruments]) &
                Q(source='google')
            ).order_by('date')

            # use data use 5:30pm close price
            stock0 = get_price(
                symbol=position_set.underlying.symbol,
                date=stop_date - BDay(1),
                source='google'
            )

            stock1 = get_price(
                symbol=position_set.underlying.symbol,
                date=stop_date,
                source='google'
            )

            if not stock1:
                raise LookupError('Please import latest price data into system.')

            if not stock0:
                stock0 = stock1

            # create position prices
            trade_price = filled_orders.first().price
            trade_quantity = filled_orders.first().quantity

            if position_set.spread == 'LONG_STOCK':
                multiplier = 1
            elif position_set.spread == 'SHORT_STOCK':
                multiplier = -1
            else:
                raise ValueError('Wrong profiler section when making calculation.')

            pl_open = (stock1.close - trade_price) * trade_quantity
            pl_open_pct = round(pl_open / (trade_price * trade_quantity) * 100 * multiplier, 2)
            pl_day = (stock1.close - stock0.close) * trade_quantity
            pl_day_pct = round(pl_day / (trade_price * trade_quantity) * 100 * multiplier, 2)

            # profit loss count
            profit_open_count = 0
            loss_open_count = 0
            profit_day_count = 0
            loss_day_count = 0

            s_pl_day = 0
            last_stock = stocks.first()
            for s in stocks:
                s_pl_open = (s.close - trade_price) * trade_quantity
                if s_pl_open > 0:
                    profit_open_count += 1
                elif s_pl_open < 0:
                    loss_open_count += 1

                if s_pl_day:
                    s_pl_day = (s.close - last_stock.close) * trade_quantity
                else:
                    s_pl_day = (s.close - trade_price) * trade_quantity

                if s_pl_day > 0:
                    profit_day_count += 1
                elif s_pl_day < 0:
                    loss_day_count += 1

                last_stock = s

            position_prices = dict(
                stock=stock1,
                stock2=stock0,
                trade_price=round(trade_price, 2),
                trade_quantity=trade_quantity,

                pl_open=pl_open,
                pl_open_pct=pl_open_pct,
                pl_day=pl_day,
                pl_day_pct=pl_day_pct,

                # pl open stat
                profit_open_count=profit_open_count,
                profit_open_count_pct=round(profit_open_count / float(len(stocks)) * 100, 2),
                loss_open_count=loss_open_count,
                loss_open_count_pct=round(loss_open_count / float(len(stocks)) * 100, 2),

                # pl day stat
                profit_day_count=profit_day_count,
                profit_day_count_pct=round(profit_day_count / float(len(stocks)) * 100, 2),
                loss_day_count=loss_day_count,
                loss_day_count_pct=round(loss_day_count / float(len(stocks)) * 100, 2),

                # stages and status
                stage=position_set.get_stage(price=stock1.close),
                status=position_set.current_status(new_price=stock1.close, old_price=stock0.close),

                # price move
                net_change=stock1.close - stock0.close,
                pct_change=(stock1.close - stock0.close) / stock0.close * 100,

                # time close and as date
                date=stop_date + Hour(17) + Minute(30),

                # holding
                holding=trade_price * trade_quantity,
                bp_effect=position_instruments.last().bp_effect,

                # price move
                pl_ytd=0,  # ytd profit loss
            )

            # create position stock, using google close data

            last_stock = stocks.first()
            for stock1 in stocks.filter(date__gte=start_date):
                net_change = 0
                pct_change = 0
                if last_stock:
                    net_change = stock1.close - last_stock.close
                    pct_change = round((stock1.close - last_stock.close) / last_stock.close * 100, 2)

                if stock1.date == stop_date and position_set.status in ['CLOSE', 'EXPIRE']:
                    stage = position_set.status
                    status = 'UNKNOWN'
                else:
                    stage = position_set.get_stage(price=stock1.close).stage_name
                    status = position_set.current_status(
                        new_price=stock1.close, old_price=last_stock.close
                    )

                position_stocks.append(
                    dict(
                        date=stock1.date,
                        open=stock1.open,
                        high=stock1.high,
                        low=stock1.low,
                        close=stock1.close,
                        net_change=net_change,
                        pct_change=pct_change,
                        pl_open=round((stock1.close - trade_price) * trade_quantity, 2),
                        pl_day=net_change * trade_quantity,
                        stage=stage,
                        status=status,
                    )
                )

                last_stock = stock1

            # create stage mover, position_stage.mover.
            position_stage_movers = dict(
                stages=position_stages,
                keys=list(),
                data=list(),
            )

            for stage in position_stages:
                if stage.price_a:
                    position_stage_movers['keys'].append('%s,%s.A $' % (stage.id, stage.stage_name))
                    position_stage_movers['keys'].append('%s,%s.A' % (stage.id, stage.stage_name))

                if stage.price_b:
                    position_stage_movers['keys'].append('%s,%s.B $' % (stage.id, stage.stage_name))
                    position_stage_movers['keys'].append('%s,%s.B' % (stage.id, stage.stage_name))

            for stock1 in stocks.filter(date__gte=start_date):
                m = dict(
                    date=stock1.date,
                    close=stock1.close
                )

                for stage in position_stages:
                    if stage.price_a:
                        m['%s,%s.A $' % (stage.id, stage.stage_name)] = stage.price_a - stock1.close
                        m['%s,%s.A' % (stage.id, stage.stage_name)] = '%+.2f (%+.2f%%)' % (
                            float(stage.price_a - stock1.close),
                            round((stage.price_a - stock1.close) / stock1.close * 100, 2)
                        )

                    if stage.price_b:
                        m['%s,%s.B $' % (stage.id, stage.stage_name)] = stage.price_b - stock1.close
                        m['%s,%s.B' % (stage.id, stage.stage_name)] = '%+.2f (%+.2f%%)' % (
                            float(stage.price_a - stock1.close),
                            round((stage.price_b - stock1.close) / stock1.close * 100, 2)
                        )

                #print mover
                position_stage_movers['data'].append(m)

            # historical symbol position stat
            historical_position_sets = PositionSet.objects.filter(
                Q(underlying__symbol=position_set.underlying.symbol)
            ).exclude(id=position_set.id)

        elif position_set.name == 'HEDGE':
            # use option get 4:30pm price
            pass
        else:
            # use option get 4:30pm price
            pass

    # previous and next
    # page navigator
    previous_item = None
    next_item = None
    first_item = None
    last_item = None
    previous_obj = position_set.positioninstrument_set\
        .filter(position_summary__date__lt=date).order_by('position_summary__date').reverse()
    if previous_obj.exists():
        first_item = previous_obj.last().position_summary.date.strftime('%Y-%m-%d')
        previous_item = previous_obj[0].position_summary.date.strftime('%Y-%m-%d')

    next_obj = position_set.positioninstrument_set\
        .filter(position_summary__date__gt=date).order_by('position_summary__date')
    if next_obj.exists():
        last_item = next_obj.last().position_summary.date.strftime('%Y-%m-%d')
        next_item = next_obj[0].position_summary.date.strftime('%Y-%m-%d')

    parameters = dict(
        position_set=position_set,
        position_dates=position_dates,
        position_stages=position_stages,
        position_instruments=position_instruments,
        position_stocks=position_stocks,
        position_stage_movers=position_stage_movers,
        historical_position_sets=historical_position_sets,
        position_prices=position_prices,

        position_opinion=position_opinion,
        position_opinions=position_opinions,

        previous=previous_item,
        next=next_item,
        first=first_item,
        last=last_item,
    )

    return render(request, template, parameters)

# todo: opinion position info 3








































