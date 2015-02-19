class Spread(object):
    def __init__(self, pos_set):
        """
        Prepare all classes
        """
        self.pos_set = pos_set
        """ :type: PositionSet """

        # name for this spread
        self.name = 'closed'

        # auto set for subclass
        self.context = 'closed'

        # status and state
        self.__status = ''

        # all pl are in list mode
        self.pls = PLS()

        # all pl in single mode
        self.pl = PL()

    def get_price(self):
        """
        Return current price for stock symbol
        :return : float
        """
        return self.pos_set.stock.mark

    price = property(fget=get_price)

    def update_status(self):
        """
        Need implement, if not return error
        """
        raise NotImplementedError(self.set_status.__name__)

    def set_status(self, status):
        """
        Normal property set status
        """
        self.__status = status

    def get_status(self):
        """
        Retrieve the status from str
        :return: str
        """
        self.update_status()

        return self.__status

    status = property(fget=get_status, fset=set_status)

    def json(self):
        """
        Need implement, if not return error
        """
        raise NotImplementedError(self.json.__name__)

    def __unicode__(self):
        """
        Need implement, if not return error
        """
        raise NotImplementedError(self.__unicode__.__name__)

    __repr__ = __str__ = __unicode__


class PLS(object):
    def __init__(self):
        """
        All pl are in list (multi)
        """
        self.start_profit = [StartProfit()]
        self.start_loss = [StartLoss()]
        self.max_profit = [MaxProfit()]
        self.max_loss = [MaxLoss()]
        self.break_even = [BreakEven()]


class PL(object):
    def __init__(self):
        """
        All pl are original (single)
        """
        self.start_profit = StartProfit()
        self.start_loss = StartLoss()
        self.max_profit = MaxProfit()
        self.max_loss = MaxLoss()
        self.break_even = BreakEven()


class BreakEven(object):
    """
    Break-even can be use for single (trend) or double (range)
    """
    def __init__(self, price=0.0, condition=''):
        """
        :param price: float
        :param condition: str
        :return:
        """
        self.price = float(price)
        self.condition = condition

    def json(self):
        """
        Return json format output
        :return: str
        """
        json = '{'
        json += '"price": "%.2f", ' % self.price
        json += '"condition": "%s"' % self.condition
        json += '}'

        return json

    def __unicode__(self):
        """
        Describe the detail of break even
        :return: str
        """
        output = '%-40s: %s %.2f' % ('Break-even when price is', self.condition, self.price)

        return output

    __str__ = __repr__ = __unicode__


class StartProfit(object):
    """
    Start profit use for greater or less
    """
    def __init__(self, price=0.0, condition=''):
        """
        Set the parameters for max profit class
        :param price: float
        :param condition: str
        """
        self.price = float(price)
        self.condition = condition

    def json(self):
        """
        Return json format output
        :return: str
        """
        json = '{'
        json += '"price": "%.2f", ' % self.price
        json += '"condition": "%s"' % self.condition
        json += '}'

        return json

    def __unicode__(self):
        """
        Describe the detail of break even
        :return: str
        """
        output = '%-40s: %s %.2f' % ('Start profit when price is',
                                     self.condition, self.price)

        return output

    __str__ = __repr__ = __unicode__


class StartLoss(object):
    """
    Start loss use for greater or less
    """
    def __init__(self, price=0.0, condition=''):
        """
        Set the parameters for max profit class
        :param price: float
        :param condition: str
        """
        self.price = float(price)
        self.condition = condition

    def json(self):
        """
        Return json format output
        :return: str
        """
        json = '{'
        json += '"price": "%.2f", ' % self.price
        json += '"condition": "%s"' % self.condition
        json += '}'

        return json

    def __unicode__(self):
        """
        Describe the detail of break even
        :return: str
        """
        output = '%-40s: %s %.2f' % ('Start loss when price is',
                                     self.condition, self.price)

        return output

    __str__ = __repr__ = __unicode__


class MaxProfit(object):
    """
    Max profit can be use for single (trend) or double (range)
    """
    def __init__(self, amount=0.0, limit=None, price=0.0, condition=''):
        """
        Set the parameters for max profit class
        :param amount: float
        :param limit: bool
        :param price: float
        :param condition: str
        """
        self.limit = limit

        if self.limit:
            self.amount = float(amount)
        else:
            self.amount = float("inf")

        self.price = float(price)
        self.condition = condition

    def json(self):
        """
        Return json format output
        :return: str
        """
        json = '{'
        json += '"amount": "%.2f", ' % self.amount
        json += '"limit": "%d", ' % (1 if self.limit else 0)
        json += '"price": "%.2f", ' % self.price
        json += '"condition": "%s"' % self.condition
        json += '}'

        return json

    def __unicode__(self):
        """
        Describe the detail of max profit
        :return: str
        """
        limit = 'LIMITED' if self.limit else 'UNLIMITED'

        output = '%-40s: %.2f (%s)\n' % ('Max profit for this trade', self.amount, limit)
        output += '%-40s: %s %.2f' % ('when price move until', self.condition, self.price)

        return output

    __str__ = __repr__ = __unicode__


class MaxLoss(object):
    """
    Max loss can be use for single (trend) or double (range)
    """
    def __init__(self, amount=0.0, limit=None, price=0.0, condition=''):
        """
        Set the parameters for max profit class
        :param amount: float
        :param limit: bool
        :param price: float
        :param condition: str
        """
        self.limit = limit

        if self.limit:
            self.amount = float(amount)
        else:
            self.amount = float("inf")

        self.price = float(price)
        self.condition = condition

    def json(self):
        """
        Return json format output
        :return: str
        """
        json = '{'
        json += '"amount": "%.2f", ' % self.amount
        json += '"limit": "%d", ' % (1 if self.limit else 0)
        json += '"price": "%.2f", ' % self.price
        json += '"condition": "%s"' % self.condition
        json += '}'

        return json

    def __unicode__(self):
        """
        Describe the detail of max loss
        :return: str
        """
        limit = 'LIMITED' if self.limit else 'UNLIMITED'

        output = '%-40s: %.2f (%s)\n' % ('Max loss for this trade', self.amount, limit)
        output += '%-40s: %s %.2f' % ('when price move until', self.condition, self.price)

        return output

    __str__ = __repr__ = __unicode__


