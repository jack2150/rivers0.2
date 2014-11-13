from lib.pos.spread import hedge


class HedgeIdentify(object):
    def __init__(self, stock, option):
        self.stock = stock
        self.option = option

        self.cls_name = None

    def long_stock(self):
        """
        Return true if long stock, false if not
        :rtype : bool
        """
        return self.stock.quantity > 0

    def short_stock(self):
        """
        Return true if short stock, false if not
        :rtype : bool
        """
        return self.stock.quantity < 0

    def long_call_option(self):
        """
        Return true if buy call option
        :return: bool
        """
        return self.option.contract == 'CALL' and self.option.quantity > 0

    def short_call_option(self):
        """
        Return true if sell call option
        :return: bool
        """
        return self.option.contract == 'CALL' and self.option.quantity < 0

    def long_put_option(self):
        """
        Return true if buy put option
        :return: bool
        """
        return self.option.contract == 'PUT' and self.option.quantity > 0

    def short_put_option(self):
        """
        Return true if sell put option
        :return: bool
        """
        return self.option.contract == 'PUT' and self.option.quantity < 0

    def is_balance(self):
        """
        Return true if stock and option are balance 1 option = 100 shares
        :return: bool
        """
        return abs(self.stock.quantity) == abs(self.option.quantity * 100)

    def get_class(self):
        """
        Return the class name use for analysis PL and etc
        :return: type
        """
        if self.long_stock() and self.short_call_option() and self.is_balance():
            # covered call
            self.cls_name = hedge.CoveredCall
        elif self.long_stock() and self.long_put_option() and self.is_balance():
            # protective put
            self.cls_name = hedge.ProtectivePut
        elif self.short_stock() and self.long_call_option() and self.is_balance():
            # protective call
            self.cls_name = hedge.ProtectiveCall
        elif self.short_stock() and self.short_put_option() and self.is_balance():
            # covered put
            self.cls_name = hedge.CoveredPut
        else:
            self.cls_name = None

        return self.cls_name



