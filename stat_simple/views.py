from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

# Create your views here.
from stat_simple.models import DayStat


@staff_member_required
def day_stat_view(request, date=''):
    template = 'admin/simple_stat/daily/index.html'

    day_stat_holdings = list()
    day_stats = DayStat.objects.order_by('statement__date').all()
    day_stat = None
    previous_item = None
    next_item = None

    if date:
        if day_stats.filter(statement__date=date).count():
            day_stat = day_stats.get(statement__date=date)
    else:
        if day_stats.count():
            day_stat = day_stats.latest('statement__date')

    if day_stat:
        date = day_stat.statement.date.strftime('%Y-%m-%d')

        names = ['EQUITY', 'OPTION', 'SPREAD', 'FUTURE', 'FOREX']
        for name in names:
            item = day_stat.daystatholding_set.filter(name=name).first()
            day_stat_holdings.append(item)

        previous_obj = day_stats.filter(statement__date__lt=date).order_by('statement__date').reverse()
        if previous_obj.exists():
            previous_item = previous_obj[0].statement.date.strftime('%Y-%m-%d')

        next_obj = day_stats.filter(statement__date__gt=date).order_by('statement__date')
        if next_obj.exists():
            next_item = next_obj[0].statement.date.strftime('%Y-%m-%d')

    parameters = dict(
        request=request,
        day_stat=day_stat,
        stat_field=[
            'name',
            'total_order', 'working_order', 'filled_order', 'cancelled_order',
            'holding', 'profit_count', 'loss_count',
            'pl_total', 'profit_total', 'loss_total',
        ],
        investment_field=day_stat_holdings,
        date=date,
        previous=previous_item,
        next=next_item
    )

    return render(request, template, parameters)