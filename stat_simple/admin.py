from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from stat_simple.models import DayStat, DayStatHolding

@staff_member_required
def date_stat_view(request, date=''):
    template = 'admin/simple_stat/daily/index.html'

    if date == '':
        date_stat = DayStat.objects.latest('statement__date')
        date = date_stat.statement.date.strftime('%Y-%m-%d')
        today_stat = DayStat.objects.filter(statement__date=date)
    else:
        today_stat = DayStat.objects.filter(statement__date=date)
        if today_stat.count():
            date_stat = today_stat.first()
            date = date_stat.statement.date.strftime('%Y-%m-%d')
        else:
            date_stat = None
            date = ''

    today_stat = today_stat.first()
    investments = list()

    if date_stat:
        names = ['equity', 'option', 'spread', 'future', 'forex']
        for name in names:
            item = today_stat.daystatholding_set.filter(name=name).first()
            investments.append(item)

    parameters = dict(
        request=request,
        date_stat=date_stat,
        stat_field=[
            'name',
            'total_order', 'working_order', 'filled_order', 'cancelled_order',
            'holding', 'profit_count', 'loss_count',
            'pl_total', 'profit_total', 'loss_total',
        ],
        investment_field=investments,
        date=date
    )

    return render(request, template, parameters)


admin.site.register(DayStat)
admin.site.register(DayStatHolding)
admin.site.register_view(
    'stat_simple/daily/$',
    urlname='app_stat_latest',
    view=date_stat_view
)
admin.site.register_view(
    'stat_simple/daily/(?P<date>\d{4}-\d{2}-\d{2})/$',
    urlname='app_stat_latest',
    view=date_stat_view
)
