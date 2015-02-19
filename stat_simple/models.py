from django.db import models
from django.db.models import Q
from tos_import.statement_account.models import AccountSummary
from tos_import.models import Statement

decimal_field = dict(max_digits=10, decimal_places=2, default=0.0)


class DayStat(models.Model):
    """
    Keep daily statistic
    """
    statement = models.ForeignKey(Statement)

    total_holding = models.IntegerField(default=0, verbose_name='Total Holding')
    total_order = models.IntegerField(default=0, verbose_name='Total Order')
    working_order = models.IntegerField(default=0, verbose_name='Working Order')
    filled_order = models.IntegerField(default=0, verbose_name='Filled Order')
    cancelled_order = models.IntegerField(default=0, verbose_name='Cancelled Order')

    account_pl_ytd = models.DecimalField(verbose_name='Account P/L YTD', **decimal_field)
    account_pl_day = models.DecimalField(verbose_name='Account P/L Day', **decimal_field)

    holding_pl_day = models.DecimalField(verbose_name='Holding P/L Day', **decimal_field)
    holding_pl_open = models.DecimalField(verbose_name='Holding P/L Open', **decimal_field)

    commission_day = models.DecimalField(verbose_name='Commission Day', **decimal_field)
    commission_ytd = models.DecimalField(verbose_name='Commission YTD', **decimal_field)
    option_bp_day = models.DecimalField(verbose_name='Option BP', **decimal_field)
    stock_bp_day = models.DecimalField(verbose_name='Stock BP', **decimal_field)

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        return '<DayStat:{date}>'.format(
            date=self.statement.date
        )


class DayStatHolding(models.Model):
    """
    keep today holding position
    """
    day_stat = models.ForeignKey(DayStat)
    # can be equity, option, spread, future or forex
    name = models.CharField(max_length=250)

    total_order = models.IntegerField(default=0, verbose_name='Total Order')
    working_order = models.IntegerField(default=0, verbose_name='Working Order')
    filled_order = models.IntegerField(default=0, verbose_name='Filled Order')
    cancelled_order = models.IntegerField(default=0, verbose_name='Cancelled Order')

    holding = models.IntegerField(default=0, verbose_name='Holding')
    profit_holding = models.IntegerField(default=0, verbose_name='Profit Count')
    loss_holding = models.IntegerField(default=0, verbose_name='Loss Count')

    pl_total = models.DecimalField(verbose_name='Total', **decimal_field)
    profit_total = models.DecimalField(verbose_name='Profit Total', **decimal_field)
    loss_total = models.DecimalField(verbose_name='Loss Total', **decimal_field)

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        return '<DayStatHolding:{date}>'.format(
            date=self.day_stat.statement.date
        )


class SaveDayStat(object):
    def __init__(self, statement):
        """
        Get data from database table and
        save it into daily stat table
        :param statement: Statement
        """
        self.statement = statement
        self.account_statement = self.statement.accountsummary_set.first()
        self.position_statement = self.statement.positionsummary_set.first()
        self.trade_activity = self.statement.tradesummary_set.first()

        self.position_future = self.position_statement.positionfuture_set
        self.position_forex = self.position_statement.positionforex_set
        self.position_instrument = self.position_statement.positioninstrument_set

        self.working_order = self.trade_activity.workingorder_set
        self.filled_order = self.trade_activity.filledorder_set
        self.cancelled_order = self.trade_activity.cancelledorder_set

    def start(self):
        """
        get all then save it into database
        """
        holdings = [
            self.get_equity(),
            self.get_option(),
            self.get_spread(),
            self.get_future(),
            self.get_forex()
        ]

        # first save daily
        day_stat = DayStat(**self.get_day_stat())
        day_stat.statement = self.statement
        day_stat.save()

        # start saving holdings
        for holding in holdings:
            ds_investment = DayStatHolding(**holding)
            ds_investment.day_stat = day_stat
            ds_investment.save()

    def get_day_stat(self):
        """
        get date stat data from table
        :return: dict
        """
        working_order = self.working_order.count()
        filled_order = self.filled_order.count()
        cancelled_order = self.cancelled_order.count()
        total_order = working_order + filled_order + cancelled_order
        total_holding = (
            self.position_forex.exclude(quantity=0).count()
            + self.position_future.exclude(quantity=0).count()
            + self.get_equity()['holding']
            + self.get_option()['holding']
            + self.get_spread()['holding']
        )

        account_pl_day = 0.0
        account_pl_ytd = 50001.00
        commission_day = 0.0
        commission_ytd = 0.0
        option_bp_day = 0.0
        stock_bp_day = 0.0
        acc = AccountSummary.objects.filter(date__lte=self.account_statement.date)
        if acc.count() >= 2:
            acc = acc.order_by('date').reverse()[:2]

            # today pl and ytd pl
            account_pl_day = float(acc.first().net_liquid_value - acc.last().net_liquid_value)
            account_pl_ytd = float(acc.first().net_liquid_value) - account_pl_ytd

            # today commission
            commission_day = float(acc.first().commissions_ytd - acc.last().commissions_ytd)
            commission_ytd = float(acc.first().commissions_ytd)

            # bp change
            option_bp_day = float(acc.first().option_buying_power - acc.last().option_buying_power)
            stock_bp_day = float(acc.first().stock_buying_power - acc.last().stock_buying_power)
        elif acc.count() == 1:
            account_pl_day = float(acc.first().net_liquid_value) - account_pl_ytd
            account_pl_ytd = float(acc.first().net_liquid_value) - account_pl_ytd

            commission_day = float(acc.first().commissions_ytd)
            commission_ytd = float(acc.first().commissions_ytd)

            option_bp_day = account_pl_ytd - float(acc.first().option_buying_power)
            stock_bp_day = (account_pl_ytd * 2) - float(acc.first().stock_buying_power)

        return dict(
            holding_pl_open=0.0,
            holding_pl_day=0.0,
            account_pl_day=account_pl_day,
            account_pl_ytd=account_pl_ytd,
            commission_day=commission_day,
            commission_ytd=commission_ytd,
            option_bp_day=option_bp_day,
            stock_bp_day=stock_bp_day,
            total_holding=total_holding,
            total_order=total_order,
            working_order=working_order,
            filled_order=filled_order,
            cancelled_order=cancelled_order
        )

    def get_future(self):
        """
        get holding future position from table
        :return: int
        """
        holding = self.position_future.exclude(pl_open=0)
        profit = self.position_future.filter(pl_open__gt=0)
        loss = self.position_future.filter(pl_open__lt=0)

        working = self.working_order.filter(contract='FUTURE').count()
        filled = self.filled_order.filter(contract='FUTURE').count()
        cancelled = self.cancelled_order.filter(contract='FUTURE').count()
        total = working + filled + cancelled

        return dict(
            name='future',
            total_order=total,
            working_order=working,
            filled_order=filled,
            cancelled_order=cancelled,
            holding=holding.count(),
            profit_holding=profit.count(),
            loss_holding=loss.count(),
            pl_total=float(sum([p.pl_open for p in holding.all()])),
            profit_total=float(sum([p.pl_open for p in profit.all()])),
            loss_total=float(sum([p.pl_open for p in loss.all()]))
        )

    def get_forex(self):
        """
        get holding forex position from table
        :return: int
        """
        holding = self.position_forex.exclude(pl_open=0)
        profit = self.position_forex.filter(pl_open__gt=0)
        loss = self.position_forex.filter(pl_open__lt=0)

        working = self.working_order.filter(contract='FOREX').count()
        filled = self.filled_order.filter(contract='FOREX').count()
        cancelled = self.cancelled_order.filter(contract='FOREX').count()
        total = working + filled + cancelled

        return dict(
            name='forex',
            total_order=total,
            working_order=working,
            filled_order=filled,
            cancelled_order=cancelled,
            holding=holding.count(),
            profit_holding=profit.count(),
            loss_holding=loss.count(),
            pl_total=float(sum([p.pl_open for p in holding.all()])),
            profit_total=float(sum([p.pl_open for p in profit.all()])),
            loss_total=float(sum([p.pl_open for p in loss.all()]))
        )

    def get_equity(self):
        """
        get holding stock position from table
        :return: int
        """
        holding = 0
        profit = 0
        loss = 0
        total = 0.0
        profit_total = 0.0
        loss_total = 0.0

        working = self.working_order.filter(contract='STOCK').count()
        filled = self.filled_order.filter(contract='STOCK').count()
        cancelled = self.cancelled_order.filter(contract='STOCK').count()
        order = working + filled + cancelled

        for position_instrument in self.position_instrument.all():
            equity = position_instrument.positionequity_set.exclude(quantity=0)
            option = position_instrument.positionoption_set.exclude(quantity=0)

            if equity.count() and not option.count():
                holding += 1
                pl_open = float(equity.first().pl_open)
                total += pl_open

                if pl_open > 0:
                    profit += 1
                    profit_total += pl_open
                elif pl_open < 0:
                    loss += 1
                    loss_total += pl_open

        return dict(
            name='equity',
            total_order=order,
            working_order=working,
            filled_order=filled,
            cancelled_order=cancelled,
            holding=holding,
            profit_holding=profit,
            loss_holding=loss,
            pl_total=total,
            profit_total=profit_total,
            loss_total=loss_total
        )

    def get_option(self):
        """
        get holding option position from table
        :return: int
        """
        holding = 0
        profit = 0
        loss = 0
        total = 0.0
        profit_total = 0.0
        loss_total = 0.0

        working = self.working_order.filter(spread='SINGLE').count()
        filled = self.filled_order.filter(spread='SINGLE').count()
        cancelled = self.cancelled_order.filter(spread='SINGLE').count()
        order = working + filled + cancelled

        for position_instrument in self.position_instrument.all():
            equity = position_instrument.positionequity_set.exclude(quantity=0)
            option = position_instrument.positionoption_set.exclude(quantity=0)

            if not equity.count() and option.count() == 1:
                holding += 1
                pl_open = float(option.first().pl_open)
                total += pl_open

                if pl_open > 0:
                    profit += 1
                    profit_total += pl_open
                elif pl_open < 0:
                    loss += 1
                    loss_total += pl_open

        return dict(
            name='option',
            total_order=order,
            working_order=working,
            filled_order=filled,
            cancelled_order=cancelled,
            holding=holding,
            profit_holding=profit,
            loss_holding=loss,
            pl_total=total,
            profit_total=profit_total,
            loss_total=loss_total
        )

    def get_spread(self):
        """
        get holding option position from table
        :return: int
        """
        holding = 0
        profit = 0
        loss = 0
        total = 0.0
        profit_total = 0.0
        loss_total = 0.0

        exclude_cond = Q(spread='FUTURE') | Q(spread='FOREX') | Q(spread='STOCK') | Q(spread='SINGLE')

        working = len(self.working_order.exclude(exclude_cond)
                      .values_list('underlying__symbol', flat=True).distinct())
        filled = len(self.filled_order.exclude(exclude_cond)
                     .values_list('underlying__symbol', flat=True).distinct())
        cancelled = len(self.cancelled_order.exclude(exclude_cond)
                        .values_list('underlying__symbol', flat=True).distinct())

        order = working + filled + cancelled

        for position_instrument in self.position_instrument.all():
            equity = position_instrument.positionequity_set.exclude(quantity=0)
            option = position_instrument.positionoption_set.exclude(quantity=0)

            if equity.count() == 0 and option.count() > 1:
                holding += 1
                pl_open = float(position_instrument.pl_open)
                total += pl_open

                if pl_open > 0:
                    profit += 1
                    profit_total += pl_open
                elif pl_open < 0:
                    loss += 1
                    loss_total += pl_open

        return dict(
            name='spread',
            total_order=order,
            working_order=working,
            filled_order=filled,
            cancelled_order=cancelled,
            holding=holding,
            profit_holding=profit,
            loss_holding=loss,
            pl_total=total,
            profit_total=profit_total,
            loss_total=loss_total
        )
