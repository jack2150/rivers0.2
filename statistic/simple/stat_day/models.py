from decimal import Decimal

from django.db import models
from django.db.models import Q

from tos_import.statement.statement_account.models import AccountSummary
from tos_import.models import Statement


decimal_field = dict(max_digits=10, decimal_places=2, default=0.0)


class StatDay(models.Model):
    """
    Keep daily statistic
    """
    statement = models.ForeignKey(Statement)

    total_holding_count = models.IntegerField(default=0, verbose_name='Total Holding')
    total_order_count = models.IntegerField(default=0, verbose_name='Total Order')
    working_order_count = models.IntegerField(default=0, verbose_name='Working Order')
    filled_order_count = models.IntegerField(default=0, verbose_name='Filled Order')
    cancelled_order_count = models.IntegerField(default=0, verbose_name='Cancelled Order')

    account_pl_ytd = models.DecimalField(verbose_name='Account P/L YTD', **decimal_field)
    account_pl_day = models.DecimalField(verbose_name='Account P/L Day', **decimal_field)

    holding_pl_day = models.DecimalField(verbose_name='Holding P/L Day', **decimal_field)
    holding_pl_open = models.DecimalField(verbose_name='Holding P/L Open', **decimal_field)

    commission_day = models.DecimalField(verbose_name='Commission Day', **decimal_field)
    commission_ytd = models.DecimalField(verbose_name='Commission YTD', **decimal_field)

    option_bp_day = models.DecimalField(verbose_name='Option BP Day', **decimal_field)
    stock_bp_day = models.DecimalField(verbose_name='Stock BP Days', **decimal_field)

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        return 'DayStat: {date}'.format(
            date=self.statement.date
        )


class StatDayHolding(models.Model):
    """
    keep today holding position
    """
    stat_day = models.ForeignKey(StatDay)
    # can be equity, option, spread, future or forex
    name = models.CharField(max_length=250)

    total_order_count = models.IntegerField(default=0, verbose_name='Total Order')
    working_order_count = models.IntegerField(default=0, verbose_name='Working Order')
    filled_order_count = models.IntegerField(default=0, verbose_name='Filled Order')
    cancelled_order_count = models.IntegerField(default=0, verbose_name='Cancelled Order')

    total_holding_count = models.IntegerField(default=0, verbose_name='Holding Count')
    profit_holding_count = models.IntegerField(default=0, verbose_name='Profit Count')
    loss_holding_count = models.IntegerField(default=0, verbose_name='Loss Count')

    pl_open_sum = models.DecimalField(verbose_name='PL Open', **decimal_field)
    profit_open_sum = models.DecimalField(verbose_name='Profit Open', **decimal_field)
    loss_open_sum = models.DecimalField(verbose_name='Loss Open', **decimal_field)

    pl_day_sum = models.DecimalField(verbose_name='PL Day', **decimal_field)
    profit_day_sum = models.DecimalField(verbose_name='Profit Day', **decimal_field)
    loss_day_sum = models.DecimalField(verbose_name='Loss Day', **decimal_field)

    bp_effect_sum = models.DecimalField(verbose_name='BP Effect Sum', **decimal_field)

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        return 'DayStatHolding: {name} {date}'.format(
            name=self.name,
            date=self.stat_day.statement.date
        )


class StatDayOptionGreek(models.Model):
    """
    Used for summarize equity, option and spread greek
    """
    stat_day_holding = models.ForeignKey(StatDayHolding)

    delta_sum = models.DecimalField(verbose_name='Delta Sum', **decimal_field)
    gamma_sum = models.DecimalField(verbose_name='Gamma Sum', **decimal_field)
    theta_sum = models.DecimalField(verbose_name='Theta Sum', **decimal_field)
    vega_sum = models.DecimalField(verbose_name='Vega Sum', **decimal_field)

    def __unicode__(self):
        return 'DayStatOptionGreek: {holding} {date}'.format(
            holding=self.stat_day_holding.name,
            date=self.stat_day_holding.stat_day.statement.date
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
        day_stat = StatDay(**self.get_day_stat())
        day_stat.statement = self.statement
        day_stat.save()

        # start saving holdings
        for holding in holdings:
            day_stat_holding = {
                key: value for key, value in holding.items() if key != 'option_greek'
            }
            ds_investment = StatDayHolding(**day_stat_holding)
            ds_investment.stat_day = day_stat
            ds_investment.save()

            if holding['name'] not in ('FUTURE', 'FOREX'):
                ds_investment.statdayoptiongreek_set.create(**holding['option_greek'])

    def get_day_stat(self):
        """
        get date stat data from table
        :return: dict
        """
        working_order_count = (
            Decimal(self.get_future()['working_order_count'])
            + Decimal(self.get_forex()['working_order_count'])
            + Decimal(self.get_equity()['working_order_count'])
            + Decimal(self.get_option()['working_order_count'])
            + Decimal(self.get_spread()['working_order_count'])
        )

        filled_order_count = (
            Decimal(self.get_future()['filled_order_count'])
            + Decimal(self.get_forex()['filled_order_count'])
            + Decimal(self.get_equity()['filled_order_count'])
            + Decimal(self.get_option()['filled_order_count'])
            + Decimal(self.get_spread()['filled_order_count'])
        )

        cancelled_order_count = (
            Decimal(self.get_future()['cancelled_order_count'])
            + Decimal(self.get_forex()['cancelled_order_count'])
            + Decimal(self.get_equity()['cancelled_order_count'])
            + Decimal(self.get_option()['cancelled_order_count'])
            + Decimal(self.get_spread()['cancelled_order_count'])
        )

        total_order_count = working_order_count + filled_order_count + cancelled_order_count

        total_holding_count = (
            self.position_forex.exclude(quantity=0).count()
            + self.position_future.exclude(quantity=0).count()
            + self.get_equity()['total_holding_count']
            + self.get_option()['total_holding_count']
            + self.get_spread()['total_holding_count']
        )
        holding_pl_day = (
            sum([p.pl_day for p in self.position_forex.exclude(quantity=0).all()])
            + sum([p.pl_day for p in self.position_future.exclude(quantity=0).all()])
        )

        holding_pl_open = (
            Decimal(self.get_future()['pl_open_sum'])
            + Decimal(self.get_forex()['pl_open_sum'])
            + Decimal(self.get_equity()['pl_open_sum'])
            + Decimal(self.get_option()['pl_open_sum'])
            + Decimal(self.get_spread()['pl_open_sum'])
        )

        account_pl_day = 0.0
        account_pl_ytd = 50001.00

        commission_day = 0.0
        commission_ytd = 0.0
        option_bp_day = 0.0
        stock_bp_day = 0.0
        acc = AccountSummary.objects.filter(date__lte=self.account_statement.date)

        if acc.count() >= 2:
            acc = acc.order_by('date').reverse()

            # today pl and ytd pl
            account_pl_day = float(acc[0].net_liquid_value - acc[1].net_liquid_value)
            account_pl_ytd = float(acc[0].net_liquid_value) - account_pl_ytd

            # today commission
            commission_day = float(acc[0].commissions_ytd - acc[1].commissions_ytd)
            commission_ytd = float(acc[0].commissions_ytd)

            # bp change
            option_bp_day = float(acc[0].option_buying_power - acc[1].option_buying_power)
            stock_bp_day = float(acc[0].stock_buying_power - acc[1].stock_buying_power)
        elif acc.count() == 1:
            account_pl_day = float(acc[0].net_liquid_value) - account_pl_ytd
            account_pl_ytd = float(acc[0].net_liquid_value) - account_pl_ytd

            commission_day = float(acc[0].commissions_ytd)
            commission_ytd = float(acc[0].commissions_ytd)

            option_bp_day = account_pl_ytd - float(acc[0].option_buying_power)
            stock_bp_day = (account_pl_ytd * 2) - float(acc[0].stock_buying_power)

        return dict(
            total_holding_count=total_holding_count,
            total_order_count=total_order_count,
            working_order_count=working_order_count,
            filled_order_count=filled_order_count,
            cancelled_order_count=cancelled_order_count,
            account_pl_ytd=account_pl_ytd,
            account_pl_day=account_pl_day,
            holding_pl_day=holding_pl_day,
            holding_pl_open=holding_pl_open,
            commission_day=commission_day,
            commission_ytd=commission_ytd,
            option_bp_day=option_bp_day,
            stock_bp_day=stock_bp_day
        )

    def get_future(self):
        """
        get holding future position from table
        :return: int
        """
        holding_position = self.position_future.exclude(pl_open=0)
        profit_position = self.position_future.filter(pl_open__gt=0)
        loss_position = self.position_future.filter(pl_open__lt=0)

        working_order_count = self.working_order.filter(contract='FUTURE').count()
        filled_order_count = self.filled_order.filter(contract='FUTURE').count()
        cancelled_order_count = self.cancelled_order.filter(contract='FUTURE').count()
        total_order_count = working_order_count + filled_order_count + cancelled_order_count

        total_holding_count = holding_position.count()
        profit_holding_count = profit_position.count()
        loss_holding_count = loss_position.count()

        pl_open_sum = float(sum([p.pl_open for p in holding_position.all()]))
        profit_open_sum = float(sum([p.pl_open for p in profit_position.all()]))
        loss_open_sum = float(sum([p.pl_open for p in loss_position.all()]))

        pl_day_sum = float(sum([p.pl_day for p in holding_position.all()]))
        profit_day_sum = float(sum([p.pl_day for p in profit_position.all()]))
        loss_day_sum = float(sum([p.pl_day for p in loss_position.all()]))

        bp_effect_sum = float(sum([p.bp_effect for p in holding_position.all()]))

        return dict(
            name='FUTURE',
            total_order_count=total_order_count,
            working_order_count=working_order_count,
            filled_order_count=filled_order_count,
            cancelled_order_count=cancelled_order_count,
            total_holding_count=total_holding_count,
            profit_holding_count=profit_holding_count,
            loss_holding_count=loss_holding_count,
            pl_open_sum=pl_open_sum,
            profit_open_sum=profit_open_sum,
            loss_open_sum=loss_open_sum,
            pl_day_sum=pl_day_sum,
            profit_day_sum=profit_day_sum,
            loss_day_sum=loss_day_sum,
            bp_effect_sum=bp_effect_sum
        )

    def get_forex(self):
        """
        get holding forex position from table
        :return: int
        """
        holding_position = self.position_forex.exclude(pl_open=0)
        profit_position = self.position_forex.filter(pl_open__gt=0)
        loss_position = self.position_forex.filter(pl_open__lt=0)

        working_order_count = self.working_order.filter(contract='FOREX').count()
        filled_order_count = self.filled_order.filter(contract='FOREX').count()
        cancelled_order_count = self.cancelled_order.filter(contract='FOREX').count()
        total_order_count = working_order_count + filled_order_count + cancelled_order_count

        total_holding_count = holding_position.count()
        profit_holding_count = profit_position.count()
        loss_holding_count = loss_position.count()

        pl_open_sum = float(sum([p.pl_open for p in holding_position.all()]))
        profit_open_sum = float(sum([p.pl_open for p in profit_position.all()]))
        loss_open_sum = float(sum([p.pl_open for p in loss_position.all()]))

        pl_day_sum = float(sum([p.pl_day for p in holding_position.all()]))
        profit_day_sum = float(sum([p.pl_day for p in profit_position.all()]))
        loss_day_sum = float(sum([p.pl_day for p in loss_position.all()]))

        bp_effect_sum = float(sum([p.bp_effect for p in holding_position.all()]))

        return dict(
            name='FOREX',
            total_order_count=total_order_count,
            working_order_count=working_order_count,
            filled_order_count=filled_order_count,
            cancelled_order_count=cancelled_order_count,
            total_holding_count=total_holding_count,
            profit_holding_count=profit_holding_count,
            loss_holding_count=loss_holding_count,
            pl_open_sum=pl_open_sum,
            profit_open_sum=profit_open_sum,
            loss_open_sum=loss_open_sum,
            pl_day_sum=pl_day_sum,
            profit_day_sum=profit_day_sum,
            loss_day_sum=loss_day_sum,
            bp_effect_sum=bp_effect_sum
        )

    def get_equity(self):
        """
        get holding stock position from table
        :return: int
        """
        total_holding_count = 0
        profit_holding_count = 0
        loss_holding_count = 0
        pl_open_sum = 0.0
        profit_open_sum = 0.0
        loss_open_sum = 0.0
        pl_day_sum = 0.0
        profit_day_sum = 0.0
        loss_day_sum = 0.0
        bp_effect_sum = 0.0

        working_order_count = self.working_order.filter(spread='STOCK').count()
        filled_order_count = self.filled_order.filter(spread='STOCK').count()
        cancelled_order_count = self.cancelled_order.filter(spread='STOCK').count()
        total_order_count = working_order_count + filled_order_count + cancelled_order_count

        position_instruments = list()
        for position_instrument in self.position_instrument.all():
            equity = position_instrument.positionequity_set.exclude(quantity=0)
            option = position_instrument.positionoption_set.exclude(quantity=0)

            if equity.count() and not option.count():
                total_holding_count += 1
                pl_open = float(equity.first().pl_open)
                pl_day = float(equity.first().pl_day)
                pl_open_sum += pl_open
                pl_day_sum += pl_day

                bp_effect_sum += float(equity.first().bp_effect)

                if pl_open > 0:
                    profit_holding_count += 1
                    profit_open_sum += pl_open
                    profit_day_sum += pl_day
                elif pl_open < 0:
                    loss_holding_count += 1
                    loss_open_sum += pl_open
                    loss_day_sum += pl_day

                position_instruments.append(position_instrument)

        option_greek = self.get_option_greek(position_instruments)

        return dict(
            name='EQUITY',
            total_order_count=total_order_count,
            working_order_count=working_order_count,
            filled_order_count=filled_order_count,
            cancelled_order_count=cancelled_order_count,
            total_holding_count=total_holding_count,
            profit_holding_count=profit_holding_count,
            loss_holding_count=loss_holding_count,
            pl_open_sum=pl_open_sum,
            profit_open_sum=profit_open_sum,
            loss_open_sum=loss_open_sum,
            pl_day_sum=pl_day_sum,
            profit_day_sum=profit_day_sum,
            loss_day_sum=loss_day_sum,
            bp_effect_sum=bp_effect_sum,
            option_greek=option_greek
        )

    def get_option(self):
        """
        get holding option position from table
        :return: int
        """
        total_holding_count = 0
        profit_holding_count = 0
        loss_holding_count = 0
        pl_open_sum = 0.0
        profit_open_sum = 0.0
        loss_open_sum = 0.0
        pl_day_sum = 0.0
        profit_day_sum = 0.0
        loss_day_sum = 0.0
        bp_effect_sum = 0.0

        working_order_count = self.working_order.filter(spread='SINGLE').count()
        filled_order_count = self.filled_order.filter(spread='SINGLE').count()
        cancelled_order_count = self.cancelled_order.filter(spread='SINGLE').count()
        total_order_count = working_order_count + filled_order_count + cancelled_order_count

        position_instruments = list()
        for position_instrument in self.position_instrument.all():
            equity = position_instrument.positionequity_set.exclude(quantity=0)
            option = position_instrument.positionoption_set.exclude(quantity=0)

            if not equity.count() and option.count() == 1:
                total_holding_count += 1
                pl_open = float(option.first().pl_open)
                pl_day = float(option.first().pl_day)
                pl_open_sum += pl_open
                pl_day_sum += pl_day
                bp_effect_sum += float(option.first().bp_effect)

                if pl_open > 0:
                    profit_holding_count += 1
                    profit_open_sum += pl_open
                    profit_day_sum += pl_day
                elif pl_open < 0:
                    loss_holding_count += 1
                    loss_open_sum += pl_open
                    loss_day_sum += pl_day

                position_instruments.append(position_instrument)

        option_greek = self.get_option_greek(position_instruments)

        return dict(
            name='OPTION',
            total_order_count=total_order_count,
            working_order_count=working_order_count,
            filled_order_count=filled_order_count,
            cancelled_order_count=cancelled_order_count,
            total_holding_count=total_holding_count,
            profit_holding_count=profit_holding_count,
            loss_holding_count=loss_holding_count,
            pl_open_sum=pl_open_sum,
            profit_open_sum=profit_open_sum,
            loss_open_sum=loss_open_sum,
            pl_day_sum=pl_day_sum,
            profit_day_sum=profit_day_sum,
            loss_day_sum=loss_day_sum,
            bp_effect_sum=bp_effect_sum,
            option_greek=option_greek
        )

    def get_spread(self):
        """
        get holding option position from table
        :return: int
        """
        total_holding_count = 0
        profit_holding_count = 0
        loss_holding_count = 0
        pl_open_sum = 0.0
        profit_open_sum = 0.0
        loss_open_sum = 0.0
        pl_day_sum = 0.0
        profit_day_sum = 0.0
        loss_day_sum = 0.0
        bp_effect_sum = 0.0

        exclude_cond = Q(spread='FUTURE') | Q(spread='FOREX') | Q(spread='STOCK') | Q(spread='SINGLE')

        working_order_count = len(self.working_order.exclude(exclude_cond)
                                  .values_list('underlying__symbol', flat=True).distinct())
        filled_order_count = len(self.filled_order.exclude(exclude_cond)
                                 .values_list('underlying__symbol', flat=True).distinct())
        cancelled_order_count = len(self.cancelled_order.exclude(exclude_cond)
                                    .values_list('underlying__symbol', flat=True).distinct())

        total_order_count = working_order_count + filled_order_count + cancelled_order_count

        position_instruments = list()
        for position_instrument in self.position_instrument.all():
            equity = position_instrument.positionequity_set.exclude(quantity=0)
            option = position_instrument.positionoption_set.exclude(quantity=0)

            if equity.count() == 0 and option.count() > 1:
                total_holding_count += 1
                pl_open = float(position_instrument.pl_open)
                pl_day = float(position_instrument.pl_day)
                pl_open_sum += pl_open
                pl_day_sum += pl_day
                bp_effect_sum += float(position_instrument.bp_effect)

                if pl_open > 0:
                    profit_holding_count += 1
                    profit_open_sum += pl_open
                    profit_day_sum += pl_day
                elif pl_open < 0:
                    loss_holding_count += 1
                    loss_open_sum += pl_open
                    loss_day_sum += pl_day

                position_instruments.append(position_instrument)

        option_greek = self.get_option_greek(position_instruments)

        return dict(
            name='SPREAD',
            total_order_count=total_order_count,
            working_order_count=working_order_count,
            filled_order_count=filled_order_count,
            cancelled_order_count=cancelled_order_count,
            total_holding_count=total_holding_count,
            profit_holding_count=profit_holding_count,
            loss_holding_count=loss_holding_count,
            pl_open_sum=pl_open_sum,
            profit_open_sum=profit_open_sum,
            loss_open_sum=loss_open_sum,
            pl_day_sum=pl_day_sum,
            profit_day_sum=profit_day_sum,
            loss_day_sum=loss_day_sum,
            bp_effect_sum=bp_effect_sum,
            option_greek=option_greek
        )

    @staticmethod
    def get_option_greek(position_instruments):
        """
        Get option for equity, option and spread
        using position instrument
        :return dict
        """
        delta_sum = Decimal(0.0)
        gamma_sum = Decimal(0.0)
        theta_sum = Decimal(0.0)
        vega_sum = Decimal(0.0)

        for instrument in position_instruments:
            delta_sum += instrument.delta
            gamma_sum += instrument.gamma
            theta_sum += instrument.theta
            vega_sum += instrument.vega

        return dict(
            delta_sum=delta_sum,
            gamma_sum=gamma_sum,
            theta_sum=theta_sum,
            vega_sum=vega_sum
        )


