from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

# Create your views here.
from statistic.simple.stat_day.models import *


@staff_member_required
def simple_stat_day_view(request, date=''):
    template = 'stat_day/index.html'

    stat_day_holdings = list()
    stat_days = StatDay.objects.order_by('statement__date').all()
    stat_day = None
    previous_item = None
    next_item = None

    if date:
        if stat_days.filter(statement__date=date).count():
            stat_day = stat_days.get(statement__date=date)
    else:
        if stat_days.count():
            stat_day = stat_days.latest('statement__date')

    if stat_day:
        # set date
        date = stat_day.statement.date.strftime('%Y-%m-%d')

        # get stat holding
        names = ['SPREAD', 'OPTION', 'EQUITY', 'FUTURE', 'FOREX']
        for name in names:
            stat_day_holding = stat_day.statdayholding_set.filter(name=name).first()

            if stat_day_holding.statdayoptiongreek_set.count():
                option_greek = stat_day_holding.statdayoptiongreek_set.first()
            else:
                option_greek = None

            stat_day_holdings.append((stat_day_holding, option_greek))








        # page navigator
        previous_obj = stat_days.filter(statement__date__lt=date).order_by('statement__date').reverse()
        if previous_obj.exists():
            previous_item = previous_obj[0].statement.date.strftime('%Y-%m-%d')

        next_obj = stat_days.filter(statement__date__gt=date).order_by('statement__date')
        if next_obj.exists():
            next_item = next_obj[0].statement.date.strftime('%Y-%m-%d')

    parameters = dict(
        request=request,
        date=date,
        stat_day=stat_day,
        stat_day_holdings=stat_day_holdings,
        previous=previous_item,
        next=next_item
    )

    return render(request, template, parameters)