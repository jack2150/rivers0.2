from django.shortcuts import render
from position.models import PositionSet
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

    position_set = PositionSet.objects.get(id=id)
    profiler_summary = dict()
    profiler_table = list()

    if position_set.underlying:
        position_instruments = position_set.positioninstrument_set.order_by(
            'position_summary__date').reverse()
        profits_losses = position_set.profitloss_set.order_by('account_summary__date').reverse()
        profiler_summary['stage'] = position_set.get_stage(
            price=position_instruments.first().positionequity.mark)
        profiler_summary['status'] = position_set.current_status(
            new_price=position_instruments.first().positionequity.mark,
            old_price=(position_instruments.first().positionequity.mark +
                       position_instruments.first().positionequity.mark_change)
        )

        # create a table
        for position_instrument, profit_loss in zip(position_instruments, profits_losses):
            # todo: next option greek, stage, status, last
            # todo: until here, wrong mark, mark change % and pl...

            profiler_table.append(
                dict(
                    date=position_instrument.position_summary.date,
                    mark=position_instrument.positionequity.mark,
                    mark_change=position_instrument.positionequity.mark_change,
                    pct_change=position_instrument.pct_change,
                    pl_open=position_instrument.pl_open,
                    pl_day=position_instrument.pl_day,
                    pl_ytd_open=profit_loss.pl_open,
                    pl_ytd_day=profit_loss.pl_day,
                    pl_ytd_pct=profit_loss.pl_pct
                )
            )

    parameters = dict(
        position_set=position_set,
        profiler_summary=profiler_summary,
        profiler_table=profiler_table
    )

    return render(request, template, parameters)












































