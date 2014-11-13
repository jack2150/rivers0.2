from lib.pos.spread.hedge import HedgeContext


class ProtectivePut(HedgeContext):
    """
    Protective Put position and calculation
    """
    def __init__(self, pos_set):
        HedgeContext.__init__(self, pos_set)

        self.name = 'protective_put'

        # start profit
        self.pl.start_profit.price = self.calc_break_even()
        self.pl.start_profit.condition = '>'

        # start loss
        self.pl.start_loss.price = self.calc_break_even()
        self.pl.start_loss.condition = '<'

        # break even
        self.pl.break_even.price = self.calc_break_even()
        self.pl.break_even.condition = '=='

        # max profit
        self.pl.max_profit.amount = float('inf')
        self.pl.max_profit.limit = False
        self.pl.max_profit.price = float('inf')
        self.pl.max_profit.condition = '=='

        # max loss
        self.pl.max_loss.amount = self.calc_max_loss()
        self.pl.max_loss.limit = True
        self.pl.max_loss.price = float(self.pos_set.option.strike_price)
        self.pl.max_loss.condition = '<='

    def calc_break_even(self):
        """
        Calculate then return break even value
        :return: float
        """
        return float(self.pos_set.stock.trade_price + self.pos_set.option.trade_price)

    def calc_max_loss(self):
        """
        Calculate then return max profit
        :return: float
        """
        return float((self.pos_set.stock.trade_price + self.pos_set.option.trade_price
                      - self.pos_set.option.strike_price) * self.pos_set.stock.quantity)