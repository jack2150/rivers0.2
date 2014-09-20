from lib.pos.spread.stock import StockContext


class StockShort(StockContext):
    """
    A spread position for long stock only
    """
    def __init__(self, pos_set):
        StockContext.__init__(self, pos_set)

        self.name = 'short_stock'

        # start profit section
        self.pl.start_profit.price = float(self.pos_set.stock.trade_price)
        self.pl.start_profit.condition = '<'

        # max profit section
        self.pl.max_profit.amount = float(self.pos_set.stock.trade_price
                                          * abs(self.pos_set.stock.quantity))
        self.pl.max_profit.limit = True
        self.pl.max_profit.price = 0
        self.pl.max_profit.condition = '=='

        # start loss section
        self.pl.start_loss.price = float(self.pos_set.stock.trade_price)
        self.pl.start_loss.condition = '>'

        # max loss section
        self.pl.max_loss.amount = float('inf')
        self.pl.max_loss.limit = False
        self.pl.max_loss.price = float('inf')
        self.pl.max_loss.condition = '=='

        # break even section
        self.pl.break_even.price = float(self.pos_set.stock.trade_price)
        self.pl.break_even.condition = '=='