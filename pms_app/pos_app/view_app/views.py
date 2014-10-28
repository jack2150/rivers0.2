from django.core.urlresolvers import reverse
from django.shortcuts import render, HttpResponse

from pms_app.pos_app import models

import datetime


# Create your views here.
def index(request, date=None):
    """
    Display the default positions views that look like tos
    :param date: str
    :param request: dict
    :return: render
    """
    if date is None:
        if models.PositionStatement.objects.exists():
            overall = models.PositionStatement.objects.last()
            date = overall.date.strftime('%Y-%m-%d')
        else:
            date = datetime.date.today()

    params = {
        'default_path': reverse('pos_view_app_index'),
        'date': date
    }

    return render(request, 'pos_view_app/index.html', params)


def date_exists(request, date):
    """
    Return 'True' if date exists and 'False' if not
    :param request: dict
    :param date: str
    :return: HttpResponse
    """
    overall = models.PositionStatement.objects.filter(date=date)

    if overall.exists():
        found = True
    else:
        found = False

    return HttpResponse(
        found,
        content_type='text/plain'
    )


def webix_js(request):
    """
    A webix components for views
    :param request:
    :return: render
    """
    return render(request, 'pos_view_app/webix.js',
                  content_type='application/javascript')


def logic_js(request):
    """
    A webix actions for views
    :param request:
    :return: render
    """
    return render(request, 'pos_view_app/logic.js',
                  content_type='application/javascript')


def overall_json(request, date=None):
    """
    Overall data in json format
    :param request: dict
    :param date: str
    :return: HttpResponse
    """
    if date:
        position_statement = models.PositionStatement.objects.filter(date=date)

        if position_statement.exists():
            position_statement = position_statement.last()
        else:
            position_statement = {}
    else:
        if models.PositionStatement.objects.exists():
            position_statement = models.PositionStatement.objects.latest('date')
        else:
            position_statement = {}

    return HttpResponse(
        position_statement,
        content_type='application/json'
    )


def positions_json(request, date=None):
    """
    Positions data (mix instrument, stock, options) in json format
    :param request: dict
    :param date: str
    :return: HttpResponse
    """
    json = list()

    if date is None and models.PositionStatement.objects.exists():
        position_statement = models.PositionStatement.objects.latest('date')
    else:
        position_statement = models.PositionStatement.objects.latest(date=date)

    if position_statement:
        positions = models.Underlying.objects.filter(position_statement=position_statement)
        instruments = models.PositionInstrument.objects.filter(position=positions)
        stocks = models.PositionStock.objects.filter(position=positions)
        options = models.PositionOption.objects.filter(position=positions)

        if positions.exists():
            for pos in positions:
                #json.append('{%s}' % instruments.get(position=pos).__str__()[1:-1])
                json.append('{%s, "data": [%s, %s]}' % (
                    instruments.get(position=pos).__str__()[1:-1],
                    stocks.get(position=pos).__str__(),
                    ','.join([option.__str__() for option in options.filter(position=pos)])
                ))

        json = '[' + ','.join(json) + ']'
    else:
        json = []

    return HttpResponse(
        json,
        content_type='application/json'
    )