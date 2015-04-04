from django.shortcuts import render
from tos_import.statement.statement_position.models \
    import PositionSummary, PositionInstrument, PositionFuture, PositionForex


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


def profiler_view(request, id=0):
    """
    Profiler view for a single position_set
    :param request: request
    :param id: int
    :return: render
    """
    template = 'position/profiler/index.html'

    parameters = dict(

    )

    return render(request, template, parameters)












































