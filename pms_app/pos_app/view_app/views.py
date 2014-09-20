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
        if models.Overall.objects.exists():
            overall = models.Overall.objects.last()
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
    overall = models.Overall.objects.filter(date=date)

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
        overall = models.Overall.objects.filter(date=date)

        if overall.exists():
            overall = overall.last()
        else:
            overall = {}
    else:
        if models.Overall.objects.exists():
            overall = models.Overall.objects.latest('date')
        else:
            overall = {}

    return HttpResponse(
        overall,
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

    if date is None:
        #date = models.Position.objects.latest('date')
        if models.Overall.objects.exists():
            date = models.Overall.objects.latest('date')
        else:
            date = datetime.date.today().strftime('%Y-%m-%d')

    positions = models.Position.objects.filter(date=date)
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

    return HttpResponse(
        json,
        content_type='application/json'
    )