from django.db import models
#from pms_app.pos_app.models import PositionStatement


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
