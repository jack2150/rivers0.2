from django.db.models import Min
from django.shortcuts import render, HttpResponse
from pms_app.pos_app import models
from lib.pos.identify import Identify


def worst_symbol(date):
    """

    :param date: str
    :return: str
    """
    # get worst position for date
    positions = models.Underlying.objects.filter(date=date)
    instruments = models.PositionInstrument.objects.filter(position=positions)
    min_pl_open = instruments.aggregate(Min('pl_open'))['pl_open__min']

    return instruments.get(pl_open=min_pl_open).underlying.symbol


def index(request, date=None):
    """

    :param request: dict
    :return: render
    """
    if date is None:
        date = models.Overall.objects.latest('date').date.strftime('%Y-%m-%d')

    params = {
        'date': date,
        'worst_symbol': worst_symbol(date)
    }

    return render(request, 'spread_view_app/index.html', params)


def webix_js(request):
    """
    A webix components for views
    :param request: dict
    :return: render
    """
    return render(request, 'spread_view_app/webix.js',
                  content_type='application/javascript')


def logic_js(request):
    """
    A webix actions for views
    :param request: dict
    :return: render
    """
    return render(request, 'spread_view_app/logic.js',
                  content_type='application/javascript')


def spreads_json(request, date=None, symbol=None):
    """
    A deep analysis for single spread
    :param request: dict
    :param date: str
    :param symbol: str
    :return: render
    """
    spreads = dict()

    if date and symbol:
        position = models.Underlying.objects.get(date=date, symbol=symbol.upper())

        spreads = dict(
            date=date,
            symbol=symbol.upper(),
            company=position.company
        )

    for key, item in spreads.items():
        spreads[key] = str(item)

    return HttpResponse(
        spreads.__str__(),
        content_type='application/json'
    )


def symbols_json(request, date):
    """
    Get positions for that date then
    make each position into spreads
    return it using json data format
    [state, status, symbol, pl_open]
    :param request: dict
    :param date: str
    :return: render json
    """
    symbols = list()

    positions = models.Underlying.objects.filter(date=date)

    for position in positions:
        pos_set = models.PositionSet(position)

        spread = Identify(pos_set).spread

        if spread:
            spread = spread(pos_set)

            symbol = '{"id": "%s", ' % str(position.symbol)
            symbol += '"symbol": "%s", ' % str(position.symbol)
            symbol += '"spread": "%s", ' % spread.name
            symbol += '"pl_open": "%.2f", ' % pos_set.instrument.pl_open
            symbol += '"status": "%s"}' % spread.status

            symbols.append(symbol)

    return HttpResponse(
        '[' + ','.join(symbols) + ']',
        content_type='application/json'
    )


# todo: spread view is a list of symbol with type of spread and pl related
# todo: not including deep analysis becuase that is for analysis view

