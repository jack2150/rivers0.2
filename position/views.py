from django.db.models import Q
from position.classes.spread.spread import Spread


class SavePositionSet(object):
    """
    Get data from filled orders and insert then into db
    """

    def __init__(self, filled_orders):
        self.filled_orders = filled_orders

    def get_underlying_symbols(self):
        """
        Get underlying symbol from filled orders
        :rtype : list
        """
        underlying_symbols = self.filled_orders.values_list(
            'underlying__symbol', flat=True).distinct()
        underlying_symbols = [str(symbol) for symbol in underlying_symbols if symbol]

        return underlying_symbols

    def get_future_symbols(self):
        """
        Get future symbol from filled orders
        :rtype : list
        """
        future_symbols = self.filled_orders.values_list(
            'future__symbol', flat=True).distinct()
        future_symbols = [str(symbol) for symbol in future_symbols if symbol]  # drop none

        return future_symbols

    def get_forex_symbols(self):
        """
        Get forex symbol from filled orders
        :rtype : list
        """
        forex_symbols = self.filled_orders.values_list(
            'forex__symbol', flat=True).distinct()
        forex_symbols = [str(symbol) for symbol in forex_symbols if symbol]

        return forex_symbols

    def save_underlying_position_set(self):
        """
        """
        underlying_symbols = self.get_underlying_symbols()

        for symbol in underlying_symbols:
            open_orders = self.filled_orders.filter(
                Q(underlying__symbol=symbol) & Q(pos_effect='TO OPEN')
            )
            if open_orders.exists():
                spread = Spread(filled_orders=open_orders)

                spread.name = spread.get_name()
                print 'Underlying: %s' % spread.get_underlying()
                print 'Name: %s' % spread.name
                print 'Spread: %s' % spread.get_spread()
                print '.' * 60

        return None

    def start(self):
        """
        Simple start
        """
        for filled_order in self.filled_orders:
            print filled_order

