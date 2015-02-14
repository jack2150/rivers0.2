from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from app_stat.models import DateStat, DateStatInvestment


@staff_member_required
def date_stat_view(request, date=''):
    #template = 'admin/app_stat/date_stat/index.html'
    template = 'admin/app_stat/date_stat/index3.html'

    if date == '':
        date_stat = DateStat.objects.latest('statement__date')
        date = date_stat.statement.date.strftime('%Y-%m-%d')
    else:
        date_stats = DateStat.objects.filter(statement__date=date)
        if date_stats.count():
            date_stat = date_stats.first()
            date = date_stat.statement.date.strftime('%Y-%m-%d')
        else:
            date_stat = None
            date = ''

    investments = list()
    if date_stat:
        names = ['equity', 'option', 'spread', 'future', 'forex']
        for name in names:
            item = DateStatInvestment.objects.filter(name=name).first()
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


admin.site.register(DateStat)
admin.site.register(DateStatInvestment)
admin.site.register_view(
    'app_stat/datestat/$',
    urlname='app_stat_latest',
    view=date_stat_view
)
admin.site.register_view(
    'app_stat/datestat/(?P<date>\d{4}-\d{2}-\d{2})/$',
    urlname='app_stat_latest',
    view=date_stat_view
)
