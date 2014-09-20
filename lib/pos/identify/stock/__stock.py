from lib.pos.spread import stock


class StockIdentify(object):
    def __init__(self, stock):
        self.stock = stock
        """:type: PositionStock"""

        self.cls_name = None

    def long_stock(self):
        """
        Return true if it is long stock and false if not
        :return: bool
        """
        return self.stock.quantity > 0

    def short_stock(self):
        """
        Return true if it is short stock and false if not
        :return: bool
        """
        return self.stock.quantity < 0

    def get_class(self):
        """
        Return the class name use for analysis PL and etc
        :return: str
        """
        if self.long_stock():
            self.cls_name = stock.StockLong
        elif self.short_stock():
            self.cls_name = stock.StockShort
        else:
            raise Exception('Invalid stock identify. Stock have zero quantity.')

        return self.cls_name