from django.db import models


class Underlying(models.Model):
    """
    A position contains 1 instrument, 1 stock and multiple options
    """
    symbol = models.CharField(max_length=10, help_text='Underlying stock symbol.')
    company = models.CharField(max_length=100, help_text='Stock company name.')

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
    symbol = models.CharField(max_length=20, verbose_name='Symbol')
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
        return '{description} {expire_date}'.format(
            description=self.description,
            expire_date=self.expire_date
        )


class Forex(models.Model):
    symbol = models.CharField(max_length=10, help_text='Forex exchange between two currency.')
    description = models.CharField(max_length=100, help_text='Description of two currency.')

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
    date = models.DateField(help_text='All statements date.')
    account_statement = models.TextField(help_text='Account statement file data.')
    position_statement = models.TextField(help_text='Position statement file data.')
    trade_activity = models.TextField(help_text='Trade activity file data.')

    def __unicode__(self):
        """
        Normal string output for class detail
        :return: str
        """
        return 'Statements: {date}'.format(
            date=self.date
        )
