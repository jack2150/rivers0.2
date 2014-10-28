from os import rename
import os
from pandas import datetime
from pandas.tseries.offsets import BDay
from django.shortcuts import render, HttpResponse
from rivers.settings import FILES
from lib.io import OpenDir, OpenPos
import pms_app.pos_app.models as pm


# Create your views here.
def index(request):
    """
    View for select positions csv files for import action with ajax completion
    :param request: dict
    :rtype : render
    """
    parameters = {
        'files': OpenDir().to_json(),
    }

    return render(request, 'pos_import_app/index.html', parameters)


def complete(request, date=None):
    """
    Ajax view for info complete insert positions into db
    :param date: str
    :param request: dict
    :rtype : render
    """
    try:
        # get path then open file
        path = OpenDir().get_path(date)
        fname = OpenDir().get_fname_from_path(path)

        # after opening, date need to minus one
        pd_date = datetime.strptime(date, '%Y-%m-%d')
        pd_date = pd_date - BDay(1)
        date = pd_date.strftime('%Y-%m-%d')

        # continues...
        positions, overall = OpenPos(path).read()

        position_statement = pm.PositionStatement(**overall)
        position_statement.date = date
        position_statement.save()

        for position in positions:
            # save underlying if not exists
            underlying_obj = pm.Underlying.objects.filter(symbol=position['Symbol'])
            if underlying_obj.exists():
                underlying = underlying_obj.first()
            else:
                underlying = pm.Underlying(
                    symbol=position['Symbol'],
                    company=position['Company']
                )
                underlying.save()

            # save instrument
            instrument = pm.PositionInstrument()
            instrument.set_dict(position['Instrument'])
            instrument.position_statement = position_statement
            instrument.underlying = underlying
            instrument.save()

            # save stock
            stock = pm.PositionStock()
            stock.set_dict(position['Stock'])
            stock.position_statement = position_statement
            stock.underlying = underlying
            stock.instrument = instrument
            stock.save()

            # save options
            for pos_option in position['Options']:
                option = pm.PositionOption()
                option.set_dict(pos_option)
                option.position_statement = position_statement
                option.underlying = underlying
                option.instrument = instrument
                option.save()

        # move files into completed folder
        rename(path, os.path.join(FILES['position_statement'], 'save', fname))

        # set parameters into templates
        parameters = {
            'date': str(date),
            'fname': str(fname)
        }

    except IOError:
        # set parameters into templates
        parameters = {
            'date': '',
            'fname': ''
        }

    return HttpResponse(
        parameters.__str__(),
        content_type='application/json'
    )


def webix_js(request):
    """
    A webix components for views
    :param request:
    :return: render
    """
    return render(request, 'pos_import_app/webix.js',
                  content_type='application/javascript')


def logic_js(request):
    """
    A webix actions for views
    :param request:
    :return: render
    """
    return render(request, 'pos_import_app/logic.js',
                  content_type='application/javascript')


def files_json(request):
    """
    Positions csv files in json format
    :param request: dict
    :return: HttpResponse
    """
    json = '[{'
    json += 'id: -1, '
    json += 'value: "Positions", '
    json += 'open: true, '
    json += 'data: %s' % OpenDir().to_json()
    json += '}]'

    return HttpResponse(
        json,
        content_type='application/json'
    )