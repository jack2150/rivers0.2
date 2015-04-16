from datetime import datetime, date
from django.db.models import Q
from django.shortcuts import render
from pandas.tseries.offsets import Day, BDay, Hour, Minute
from data.models import Stock, get_price
from position.models import PositionSet
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


def profiler_view(request, position_set_id=0):
    """
    Profiler view for a single position_set
    :param request: request
    :param position_set_id: int
    :return: render
    """
    template = 'position/profiler/index.html'

    # get position set and position stages
    position_set = PositionSet.objects.get(id=position_set_id)
    position_stages = position_set.positionstage_set.all()

    # display variables
    position_prices = dict()
    position_stocks = list()
    position_stage_movers = list()
    historical_position_sets = None

    # foreign keys
    filled_orders = position_set.filledorder_set.order_by('trade_summary__date').all()
    position_instruments = position_set.positioninstrument_set.order_by('position_summary__date').all()

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
            stock = get_price(
                symbol=position_set.underlying.symbol,
                date=stop_date,
                source='google'
            )

            stock2 = get_price(
                symbol=position_set.underlying.symbol,
                date=stop_date - BDay(1),
                source='google'
            )

            if not stock:
                raise LookupError('Please import latest price data into system.')

            if not stock2:
                stock2 = stock

            # create position prices
            trade_price = filled_orders.first().price
            trade_quantity = filled_orders.first().quantity

            if position_set.spread == 'LONG_STOCK':
                multiplier = 1
            elif position_set.spread == 'SHORT_STOCK':
                multiplier = -1
            else:
                raise ValueError('Wrong profiler section when making calculation.')

            pl_open = (stock.close - trade_price) * trade_quantity
            pl_open_pct = round(pl_open / (trade_price * trade_quantity) * 100 * multiplier, 2)
            pl_day = (stock.close - stock2.close) * trade_quantity
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
                stock=stock,
                stock2=stock2,
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
                stage=position_set.get_stage(price=stock.close),
                status=position_set.current_status(new_price=stock.close, old_price=stock2.close),

                # price move
                net_change=stock.close - stock2.close,
                pct_change=(stock.close - stock2.close) / stock2.close * 100,

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
            for stock in stocks.filter(date__gte=start_date):
                net_change = 0
                pct_change = 0
                if last_stock:
                    net_change = stock.close - last_stock.close
                    pct_change = round((stock.close - last_stock.close) / last_stock.close * 100, 2)

                if stock.date == stop_date and position_set.status in ['CLOSE', 'EXPIRE']:
                    stage = position_set.status
                    status = 'UNKNOWN'
                else:
                    stage = position_set.get_stage(price=stock.close).stage_name
                    status = position_set.current_status(
                        new_price=stock.close, old_price=last_stock.close
                    )

                position_stocks.append(
                    dict(
                        date=stock.date,
                        open=stock.open,
                        high=stock.high,
                        low=stock.low,
                        close=stock.close,
                        net_change=net_change,
                        pct_change=pct_change,
                        pl_open=round((stock.close - trade_price) * trade_quantity, 2),
                        pl_day=net_change * trade_quantity,
                        stage=stage,
                        status=status,
                    )
                )

                last_stock = stock

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

            for stock in stocks.filter(date__gte=start_date):
                m = dict(
                    date=stock.date,
                    close=stock.close
                )

                for stage in position_stages:
                    if stage.price_a:
                        m['%s,%s.A $' % (stage.id, stage.stage_name)] = stage.price_a - stock.close
                        m['%s,%s.A' % (stage.id, stage.stage_name)] = '%+.2f (%+.2f%%)' % (
                            float(stage.price_a - stock.close),
                            round((stage.price_a - stock.close) / stock.close * 100, 2)
                        )

                    if stage.price_b:
                        m['%s,%s.B $' % (stage.id, stage.stage_name)] = stage.price_b - stock.close
                        m['%s,%s.B' % (stage.id, stage.stage_name)] = '%+.2f (%+.2f%%)' % (
                            float(stage.price_a - stock.close),
                            round((stage.price_b - stock.close) / stock.close * 100, 2)
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

    parameters = dict(
        position_set=position_set,
        position_dates=position_dates,
        position_stages=position_stages,
        position_instruments=position_instruments,
        position_stocks=position_stocks,
        position_stage_movers=position_stage_movers,
        historical_position_sets=historical_position_sets,

        position_prices=position_prices,
    )

    return render(request, template, parameters)












































