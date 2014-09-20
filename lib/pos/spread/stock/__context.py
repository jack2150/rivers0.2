from lib.pos.spread import Spread


class StockContext(Spread):
    def __init__(self, pos_set):
        # parent init
        Spread.__init__(self, pos_set)

        # set context
        self.context = 'stock'

        # remove pls
        self.pls = None
        """ :type: None """

    def is_profit(self, price):
        """
        Return true if position is profit and false if not
        :return: bool
        """
        return eval('%s %s %s' % (
            price,
            self.pl.start_profit.condition,
            self.pl.start_profit.price
        ))

    def is_loss(self, price):
        """
        Return true if position is losing and false if not
        :return: bool
        """
        return eval('%s %s %s' % (
            price,
            self.pl.start_loss.condition,
            self.pl.start_loss.price
        ))

    def is_even(self, price):
        """
        Return true if position is even and false if not
        :return: bool
        """
        return eval('%s %s %s' % (
            price,
            self.pl.break_even.condition,
            self.pl.break_even.price
        ))

    def update_status(self):
        """
        Return true if price is already profit
        """
        if self.is_even(self.price):
            self.status = 'even'
        elif self.is_profit(self.price):
            self.status = 'profit'
        elif self.is_loss(self.price):
            self.status = 'loss'

    def json(self):
        """
        Return stock data in json format
        :return: str
        """
        json = '{'
        json += '"context": "%s", ' % self.context
        json += '"name": "%s", ' % self.name
        json += '"start_profit": %s, ' % self.pl.start_profit.json()
        json += '"start_loss": %s, ' % self.pl.start_loss.json()
        json += '"break_even": %s' % self.pl.break_even.json()
        json += '}'

        return json

    def __unicode__(self):
        """
        Describe stock position
        :return: str
        """
        output = '%s Stock Position:\n' % self.name
        output += '%s\n' % self.pl.break_even
        output += '%s\n' % self.pl.start_profit
        output += '%s\n' % self.pl.start_loss
        output += '%s\n' % self.pl.max_profit
        output += '%s' % self.pl.max_loss

        return output

    __repr__ = __str__ = __unicode__