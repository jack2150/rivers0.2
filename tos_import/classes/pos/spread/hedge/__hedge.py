from lib.pos.spread import Spread


class HedgeContext(Spread):
    def __init__(self, pos_set):
        # parent init
        Spread.__init__(self, pos_set)

        # set context
        self.context = 'hedge'

        # remove pls
        self.pls = None

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

    def is_profit(self, price):
        """
        Return true if position is profit and false if not
        :return: bool
        """
        return eval('%s %s float("%s")' % (
            price,
            self.pl.start_profit.condition,
            self.pl.start_profit.price
        ))

    def is_loss(self, price):
        """
        Return true if position is losing and false if not
        :return: bool
        """
        return eval('%s %s float("%s")' % (
            price,
            self.pl.start_loss.condition,
            self.pl.start_loss.price
        ))

    def is_max_profit(self, price):
        """
        Return true if position is in max profit and false if not
        :return: bool
        """
        return eval('%s %s float("%s")' % (
            price,
            self.pl.max_profit.condition,
            self.pl.max_profit.price
        ))

    def is_max_loss(self, price):
        """
        Return true if position is in max loss and false if not
        :return: bool
        """
        return eval('%s %s float("%s")' % (
            price,
            self.pl.max_loss.condition,
            self.pl.max_loss.price
        ))

    def update_status(self):
        """
        Return true if price is already profit
        """
        if self.is_even(self.price):
            self.status = 'even'
        elif self.is_max_profit(self.price):
            self.status = 'max_profit'
        elif self.is_profit(self.price):
            self.status = 'profit'
        elif self.is_max_loss(self.price):
            self.status = 'max_loss'
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
        json += '"max_profit": %s, ' % self.pl.max_profit.json()
        json += '"max_loss": %s, ' % self.pl.max_loss.json()
        json += '"break_even": %s' % self.pl.break_even.json()
        json += '}'

        return json

    def __unicode__(self):
        """
        Describe hedge position
        :return: str
        """
        output = '%s Position:\n' % self.name
        output += '%s\n' % self.pl.start_profit
        output += '%s\n' % self.pl.max_profit
        output += '%s\n' % self.pl.start_loss
        output += '%s\n' % self.pl.max_loss
        output += '%s\n' % self.pl.break_even

        return output

    __str__ = __repr__ = __unicode__
