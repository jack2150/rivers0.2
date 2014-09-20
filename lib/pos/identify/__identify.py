from lib.pos.identify import stock, hedge, leg_one


class Identify(object):
    def __init__(self, pos_set):
        """
        Set stock and options at init
        :param pos_set: pms_app.classes.position_set.PositionSet
        """
        self.pos_set = pos_set
        """ :type: PositionSet """

        self.__spread = None

    def get_spread(self):
        """
        Return string for identify spreads type
        :return: str
        """
        if self.__spread is None:
            self.identify()

        return self.__spread

    def set_spread(self, x):
        """
        Set string into spreads type name
        :param x: str
        """
        self.__spread = x

    spread = property(fget=get_spread, fset=set_spread)

    def identify(self):
        """
        Check how many legs, quantity, strike and etc...
        1. find which type and legs
        2. go to deep identify then decide strategy
        3. then go to strategy to define pl and etc
        """
        if self.is_closed():
            #self.__spread = 'Position Closed'
            self.__spread = None
        elif self.is_stock():
            #self.__name = 'Stock Position'
            self.__spread = stock.StockIdentify(self.pos_set.stock).get_class()
        elif self.is_hedge():
            #self.__name = 'Hedge Position'
            self.__spread = hedge.HedgeIdentify(self.pos_set.stock, self.pos_set.option).get_class()
        elif self.is_one_leg():
            #self.__name = 'One Leg Options'
            self.__spread = leg_one.LegOneIdentify(self.pos_set.option).get_class()
        elif self.is_two_legs():
            #self.__spread = 'Two Legs Options'
            self.__spread = None
        elif self.is_three_legs():
            #self.__spread = 'Three Legs Options'
            self.__spread = None
        elif self.is_four_legs():
            #self.__spread = 'Four Legs Options'
            self.__spread = None
        else:
            #self.__spread = 'Custom Options'
            self.__spread = None

    def is_closed(self):
        """
        Return true if positions is closed and false if not
        :return: bool
        """
        return bool(not self.pos_set.stock.quantity and not self.pos_set.options.count())

    def is_stock(self):
        """
        Return true if positions is stock and if not false
        :rtype : bool
        """
        return bool(self.pos_set.stock.quantity and not self.pos_set.options.count())

    def is_hedge(self):
        """
        Return true if hedge positions (stock + options) and false if not
        :return: bool
        """
        return bool(self.pos_set.stock.quantity and self.pos_set.options.count() == 1)

    def is_one_leg(self):
        """
        Return true if one leg option only positions and false if not
        :return: bool
        """
        return bool(not self.pos_set.stock.quantity and self.pos_set.options.count() == 1)

    def is_two_legs(self):
        """
        Return true if two legs option positions and false if not
        :return: bool
        """
        return bool(not self.pos_set.stock.quantity and self.pos_set.options.count() == 2)

    def is_three_legs(self):
        """
        Return true if three legs option positions and false if not
        :return: bool
        """
        return bool(not self.pos_set.stock.quantity and self.pos_set.options.count() == 3)

    def is_four_legs(self):
        """
        Return true if two legs option positions and false if not
        :return: bool
        """
        return bool(not self.pos_set.stock.quantity and self.pos_set.options.count() == 4)