from django.db import models
from app_pms.classes.io import OpenPos
from app_pms.models import Underlying, Statement, SaveAppModel, Future, Forex


class PositionModel(object):
    def set_dict(self, items):
        """
        using raw dict, set related column into property only
        :type items: dict
        """
        properties = vars(self)

        for key, item in items.items():
            if key in properties.keys():
                setattr(self, key, item)


class PositionStatement(models.Model):
    """
    A position statement contain date and overall data
    """
    statement = models.ForeignKey(Statement)
    date = models.DateField(unique=True, verbose_name="Date")
    cash_sweep = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Cash Sweep"
    )
    pl_ytd = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="P/L YTD"
    )
    futures_bp = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="BP ADJUST"
    )
    bp_adjustment = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="FUTURES BP"
    )
    available = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="AVAILABLE $"
    )

    def json(self):
        """
        use all property and output json format string
        """
        output = '{'
        output += '"date": "%s", ' % self.date
        output += '"cash_sweep": %.2f, ' % self.cash_sweep
        output += '"pl_ytd": %.2f, ' % self.pl_ytd
        output += '"futures_bp": %.2f, ' % self.futures_bp
        output += '"bp_adjustment": %.2f, ' % self.bp_adjustment
        output += '"available": %.2f' % self.available
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        position_statement = '<PositionStatement:{date}> {pl_ytd}'

        return '{position_statement}'.format(
            position_statement=position_statement.format(
                date='%s' % self.date,
                pl_ytd='%+.2f' % self.pl_ytd,
            )
        )

    class Meta:
        verbose_name_plural = "   Position Statements"


class PositionInstrument(models.Model, PositionModel):
    position_statement = models.ForeignKey(PositionStatement)
    underlying = models.ForeignKey(Underlying)

    delta = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Delta")
    gamma = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Gamma")
    theta = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Theta")
    vega = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Vega")
    pct_change = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Pct Change")
    pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="PL Open")
    pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="PL Day")
    bp_effect = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="BP Effect")

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"name": "%s", ' % self.underlying.company
        output += '"quantity": 0, '
        output += '"days": 0, '
        output += '"trade_price": 0, '
        output += '"mark": 0, '
        output += '"mark_change": 0, '
        output += '"delta": %.2f, ' % self.delta
        output += '"gamma": %.2f, ' % self.gamma
        output += '"theta": %.2f, ' % self.theta
        output += '"vega": %.2f, ' % self.vega
        output += '"pct_change": %.2f, ' % self.pct_change
        output += '"pl_open": %.2f, ' % self.pl_open
        output += '"pl_day": %.2f, ' % self.pl_day
        output += '"bp_effect": %.2f' % self.bp_effect
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for model detail
        :return: str
        """
        return '<PositionInstrument:{date}> {symbol}'.format(
            date=self.position_statement.date,
            symbol=self.underlying.symbol
        )

    class Meta:
        verbose_name_plural = "  Instruments"


class PositionEquity(models.Model, PositionModel):
    position_statement = models.ForeignKey(PositionStatement)
    underlying = models.ForeignKey(Underlying)
    instrument = models.ForeignKey(PositionInstrument)

    quantity = models.IntegerField(default=0, verbose_name="Quantity")
    trade_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Trade Price")
    mark = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Mark")
    mark_change = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Mark Change")
    pct_change = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Pct Change")
    pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="PL Open")
    pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="PL Day")
    bp_effect = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="BP Effect")

    def json(self):
        output = '{'
        output += '"name": "%s", ' % self.underlying.symbol
        output += '"quantity": %+d, ' % self.quantity
        output += '"days": 0, '
        output += '"trade_price": %.2f, ' % self.trade_price
        output += '"mark": %.2f, ' % self.mark
        output += '"mark_change": %.2f, ' % self.mark_change
        output += '"delta": 0, '
        output += '"gamma": 0, '
        output += '"theta": 0, '
        output += '"vega": 0, '
        output += '"pct_change": %.2f, ' % self.pct_change
        output += '"pl_open": %.2f, ' % self.pl_open
        output += '"pl_day": %.2f, ' % self.pl_day
        output += '"bp_effect": %.2f' % self.bp_effect
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for model detail
        :return: str
        """
        return '<PositionEquity:{date}> {symbol}'.format(
            date=self.position_statement.date,
            symbol=self.underlying.symbol,
        )

    class Meta:
        verbose_name_plural = " Stock"


class PositionOption(models.Model):
    position_statement = models.ForeignKey(PositionStatement)
    underlying = models.ForeignKey(Underlying)
    instrument = models.ForeignKey(PositionInstrument)

    # option contract name
    right = models.IntegerField(default=100, verbose_name="Right")
    special = models.CharField(max_length=100, verbose_name="Special")
    ex_month = models.CharField(max_length=10, verbose_name="Expire Month")
    ex_year = models.IntegerField(verbose_name="Expire Year")
    strike = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Strike")
    contract = models.CharField(max_length=10, verbose_name="Contract")

    # position details
    quantity = models.IntegerField(default=0, verbose_name="Quantity")
    days = models.IntegerField(default=0, verbose_name="DTE")
    trade_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Trade Price")
    mark = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Mark")
    mark_change = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Mark Change")
    delta = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Delta")
    gamma = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Gamma")
    theta = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Theta")
    vega = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Vega")
    pct_change = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="Percent Change")
    pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="PL Open")
    pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="PL Day")
    bp_effect = models.DecimalField(max_digits=8, decimal_places=2, default=0.0, verbose_name="BP Effect")

    def set_dict(self, items):
        """
        using raw dict, set related column into property only
        :type items: dict
        """
        properties = vars(self)

        for key, item in items.items():
            if key in properties.keys():
                setattr(self, key, item)

            if key == 'name':
                # assign options name
                for sub_key, sub_item in item.items():
                    if sub_key in properties.keys():
                        setattr(self, sub_key, sub_item)

    def json(self):
        """
        use all property and output json format string
        """
        # prepare options name
        options = '%s %s %s %s %s %s' % (
            self.right,
            self.special,
            self.ex_month,
            self.ex_year,
            self.strike,
            self.contract
        )

        # ready output
        output = '{'
        output += '"name": "%s", ' % options
        output += '"quantity": %d, ' % self.quantity
        output += '"days": %d, ' % self.days
        output += '"trade_price": %.2f, ' % self.trade_price
        output += '"mark": %.2f, ' % self.mark
        output += '"mark_change": %.2f, ' % self.mark_change
        output += '"delta": %.2f, ' % self.delta
        output += '"gamma": %.2f, ' % self.gamma
        output += '"theta": %.2f, ' % self.theta
        output += '"vega": %.2f, ' % self.vega
        output += '"pct_change": %.2f, ' % self.pct_change
        output += '"pl_open": %.2f, ' % self.pl_open
        output += '"pl_day": %.2f, ' % self.pl_day
        output += '"bp_effect": 0'
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for model detail
        :return: str
        """
        option = '{symbol} {right} {special} {ex_month} {ex_year} {strike_price} {contract}'

        return '<PositionOption:{date}> {option}'.format(
            date=self.position_statement.date,
            option=option.format(
                symbol=self.underlying.symbol,
                right=self.right,
                special=self.special,
                ex_month=self.ex_month,
                ex_year=self.ex_year,
                strike_price=self.strike,
                contract=self.contract
            )
        )

    class Meta:
        verbose_name_plural = "Option"


class PositionFuture(models.Model, PositionModel):
    position_statement = models.ForeignKey(PositionStatement, verbose_name='Position Statement')
    future = models.ForeignKey(Future, verbose_name='Future')

    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    days = models.IntegerField(default=0, verbose_name='Days')
    trade_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="Trade Price"
    )
    mark = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="Mark"
    )
    mark_change = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="Mark Change"
    )
    pct_change = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="Percent Change"
    )
    pl_open = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="P/L Open"
    )
    pl_day = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="P/L Day"
    )
    bp_effect = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="BP Effect"
    )

    def json(self):
        output = '{'
        output += '"symbol": "/%s", ' % self.future.lookup
        output += '"quantity": %+d, ' % self.quantity
        output += '"days": %d, ' % self.days
        output += '"trade_price": %.2f, ' % self.trade_price
        output += '"mark": %.2f, ' % self.mark
        output += '"mark_change": %.2f, ' % self.mark_change
        output += '"pct_change": %.2f, ' % self.pct_change
        output += '"pl_open": %.2f, ' % self.pl_open
        output += '"pl_day": %.2f, ' % self.pl_day
        output += '"bp_effect": %.2f' % self.bp_effect
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for model detail
        :return: str
        """
        return '<PositionFuture:{date}> /{symbol}'.format(
            date=self.position_statement.date,
            symbol=self.future.lookup
        )


class PositionForex(models.Model, PositionModel):
    position_statement = models.ForeignKey(PositionStatement, verbose_name='Position Statement')
    forex = models.ForeignKey(Forex, verbose_name='Forex')

    quantity = models.IntegerField(default=0, verbose_name='Quantity')
    trade_price = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="Trade Price"
    )
    mark = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="Mark"
    )
    mark_change = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="Mark Change"
    )
    pct_change = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="Percent Change"
    )
    pl_open = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="P/L Open"
    )
    pl_day = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="P/L Day"
    )
    bp_effect = models.DecimalField(
        max_digits=8, decimal_places=2, default=0.0, verbose_name="BP Effect"
    )

    def json(self):
        output = '{'
        output += '"symbol": "%s", ' % self.forex.symbol
        output += '"quantity": %+d, ' % self.quantity
        output += '"trade_price": %.2f, ' % self.trade_price
        output += '"mark": %.2f, ' % self.mark
        output += '"mark_change": %.2f, ' % self.mark_change
        output += '"pct_change": %.2f, ' % self.pct_change
        output += '"pl_open": %.2f, ' % self.pl_open
        output += '"pl_day": %.2f, ' % self.pl_day
        output += '"bp_effect": %.2f' % self.bp_effect
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for model detail
        :return: str
        """
        return '<PositionForex:{date}> {symbol}'.format(
            date=self.position_statement.date,
            symbol=self.forex.symbol
        )


class SavePositionStatement(SaveAppModel):
    def __init__(self, date, statement, file_data):
        """
        :param date: str
        :param statement: Statement
        :param file_data: str, raw file read
        """
        SaveAppModel.__init__(self, date, statement, file_data)

        pos_data = OpenPos(data=self.file_data).read()

        self.equity_option_position = pos_data['equity_option_position']
        self.future_position = pos_data['future_position']
        self.forex_position = pos_data['forex_position']
        self.position_summary = pos_data['position_summary']

        self.position_statement = None

    def save_position_statement(self):
        """
        Save position statement into db
        """
        self.position_statement = PositionStatement(
            statement=self.statement,
            date=self.date,
            **self.position_summary
        )
        self.position_statement.save()

    def save_future_position(self):
        """
        Save future position into db
        """
        for future_position in self.future_position:
            future = self.get_future(
                lookup=future_position['lookup'],
                symbol=future_position['symbol'],
                description=future_position['description'],
                expire_date=future_position['expire_date'],
                session=future_position['session'],
                spc=future_position['spc']
            )

            pos_future = PositionFuture(
                position_statement=self.position_statement,
                future=future
            )
            pos_future.set_dict(future_position)
            pos_future.save()

    def save_forex_position(self):
        """
        Save forex position into db
        """
        for forex_position in self.forex_position:
            forex = self.get_forex(symbol=forex_position['symbol'])

            pos_forex = PositionForex(
                position_statement=self.position_statement,
                forex=forex
            )
            pos_forex.set_dict(forex_position)
            pos_forex.save()

    def save_equity_option_position(self):
        """
        Save instrument, equity, option into db
        """
        for equity_option_position in self.equity_option_position:
            underlying = self.get_underlying(
                symbol=equity_option_position['symbol'],
                company=equity_option_position['company']
            )

            pos_instrument = PositionInstrument(
                position_statement=self.position_statement,
                underlying=underlying
            )
            pos_instrument.set_dict(equity_option_position['instrument'])
            pos_instrument.save()

            pos_equity = PositionEquity(
                position_statement=self.position_statement,
                underlying=underlying,
                instrument=pos_instrument
            )
            pos_equity.set_dict(equity_option_position['equity'])
            pos_equity.save()

            for option in equity_option_position['options']:
                pos_option = PositionOption(
                    position_statement=self.position_statement,
                    underlying=underlying,
                    instrument=pos_instrument
                )
                pos_option.set_dict(option)
                pos_option.save()

    def save_all(self):
        """
        Save all data into position models
        """
        self.save_position_statement()
        self.save_equity_option_position()
        self.save_future_position()
        self.save_forex_position()