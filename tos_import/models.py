from django.db import models


class Underlying(models.Model):
    """
    A position contains 1 instrument, 1 stock and multiple options
    """
    symbol = models.CharField(max_length=10, help_text='Underlying stock symbol.')
    company = models.CharField(max_length=100, null=True, blank=True, help_text='Stock company name.')

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"symbol": "%s", ' % self.symbol
        output += '"company": "%s"' % self.company
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        return '{symbol}'.format(
            symbol=self.symbol
        )


class Future(models.Model):
    """
    A future that have 4 session per year and different symbol
    """
    symbol = models.CharField(max_length=20, blank=True, null=True, verbose_name='Symbol')
    lookup = models.CharField(max_length=2, blank=True, null=True, verbose_name='Lookup')
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name='Description')
    expire_date = models.CharField(max_length=20, blank=True, null=True, verbose_name='Expire Date')
    session = models.CharField(max_length=20, blank=True, null=True, verbose_name='Session')
    spc = models.CharField(max_length=20, blank=True, null=True, verbose_name='Shares Per Contract')

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"lookup": "%s", ' % self.lookup
        output += '"symbol": "%s", ' % self.symbol
        output += '"description": "%s", ' % self.description
        output += '"expire_date": "%s", ' % self.expire_date
        output += '"session": "%s", ' % self.session
        output += '"spc": "%s"' % self.spc
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        if self.symbol:
            symbol = self.symbol
        else:
            symbol = '/%s' % self.lookup

        return '{symbol}'.format(
            symbol=symbol
        )


class Forex(models.Model):
    symbol = models.CharField(max_length=10, help_text='Forex exchange between two currency.')
    description = models.CharField(
        max_length=100, null=True, blank=True, help_text='Description of two currency.'
    )

    def json(self):
        """
        Using all property inside class and return json format string
        :return: str
        """
        output = '{'
        output += '"symbol": "%s", ' % self.symbol
        output += '"description": "%s"' % self.description
        output += '}'

        return output

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        return '{symbol}'.format(
            symbol=self.symbol
        )


class Statement(models.Model):
    """
    A statement contain all 3 raw files csv data including
    account statement, position statement and trade activity
    """
    date = models.DateField(unique=True)
    account_statement = models.TextField()
    position_statement = models.TextField()
    trade_activity = models.TextField()

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        return 'Statements: {date}'.format(
            date=self.date
        )


class SaveAppModel(object):
    def __init__(self, date, statement, file_data):
        """
        :param date: str
        :param statement: Statement
        :param file_data: str, raw file read
        """
        self.date = date
        self.statement = statement
        self.file_data = file_data

        # get all underlying, fast query speed
        self.underlying = Underlying.objects.all()
        self.future = Future.objects.all()
        self.forex = Forex.objects.all()

    def get_underlying(self, symbol, company=''):
        """
        Return saved underlying object from db
        if not exists, save new underlying then return
        :param symbol: str
        :param company: object
        :rtype : Underlying
        """
        if self.underlying.filter(symbol=symbol).count():
            underlying = self.underlying.get(symbol=symbol)

            if underlying.company == '':
                underlying.company = company
                underlying.save()
        else:
            underlying = Underlying(
                symbol=symbol,
                company=company
            )
            underlying.save()
            self.underlying = Underlying.objects.all()

        return underlying

    def get_future(self, symbol, lookup='', description='',
                   expire_date='', session='', spc=''):
        """
        Return a future object that have already saved in db
        :param symbol: str
        :param lookup: str
        :param description: str
        :param expire_date: str
        :param session:  str
        :param spc: str
        :return: Future
        """
        if lookup:
            if symbol:
                found = self.future.filter(symbol=symbol, lookup=lookup)
            else:
                found = self.future.filter(lookup=lookup)
        else:
            found = self.future.filter(symbol=symbol)

        if found.count():
            future = found.last()

            if future.symbol == '' and symbol:
                future.symbol = symbol

            if future.lookup == '' and lookup:
                future.lookup = lookup

            if future.description == '' and description:
                future.description = description

            if future.expire_date == '' and expire_date:
                future.expire_date = expire_date

            if future.session == '' and session:
                future.session = session

            if future.spc == '' and spc:
                future.spc = spc

            future.save()
        else:
            future = Future(
                lookup=lookup,
                symbol=symbol,
                description=description,
                expire_date=expire_date,
                session=session,
                spc=spc
            )
            future.save()
            self.future = Future.objects.all()

        return future

    def get_forex(self, symbol, description=''):
        """
        Return saved underlying object from db
        if not exists, save new underlying then return
        :param symbol: str
        :param description: str
        :rtype : Forex
        """
        if self.forex.filter(symbol=symbol).count():
            forex = self.forex.get(symbol=symbol)

            if forex.description == '':
                forex.description = description
                forex.save()
        else:
            forex = Forex(
                symbol=symbol,
                description=description
            )
            forex.save()
            self.forex = Forex.objects.all()

        return forex