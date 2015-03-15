from django.db.models import Q
from importlib import import_module
from position.classes.spread.spread import Spread
from position.models import PositionSet, PositionContext, PositionContexts


class PositionSetManager(object):
    """
    usage: PositionSetManager.update.update_position_instruments(x)


    position_set.manager.update.position_instruments()
    adv: auto update all dates
    dis: hard to test, ref problem
    """
    # noinspection PyPep8Naming
    class update(object):
        """
        Take a list of
            PositionInstrument,
            PositionFuture,
            PositionForex,
            Profit_Loss
        then add foreign key position set
        """
        @staticmethod
        def position_instruments(position_instruments):
            """
            Input a list of position instruments
            and update set corresponding position set
            :param position_instruments: PositionInstrument
            :rtype : PositionInstrument
            """
            for position_instrument in position_instruments:
                position_set = PositionSet.objects.filter(
                    Q(underlying=position_instrument.underlying) & Q(status='Open')
                )

                # if not found, it was closed
                if position_set.exists():
                    position_instrument.position_set = position_set.first()
                    position_instrument.save()

            return position_instruments

        @staticmethod
        def position_futures(position_futures):
            """
            Input a list of position futures
            and update set corresponding position set
            :param position_futures: PositionFuture
            :rtype : PositionFuture
            """
            for position_future in position_futures:
                position_set = PositionSet.objects.filter(
                    Q(underlying=position_future.future) & Q(status='Open')
                )

                if position_set.exists():
                    position_future.position_set = position_set.first()
                    position_future.save()

            return position_futures

        @staticmethod
        def position_forexs(position_forexs):
            """
            Input a list of position forexs
            and update set corresponding position set
            :param position_forexs: PositionForex
            :rtype : PositionForex
            """
            for position_forex in position_forexs:
                position_set = PositionSet.objects.filter(
                    Q(underlying=position_forex.forex) & Q(status='Open')
                )

                if position_set.exists():
                    position_forex.position_set = position_set.first()
                    position_forex.save()

            return position_forexs

        @staticmethod
        def profits_losses(profits_losses):
            """
            Input a list of profit loss
            and update set corresponding position set
            :param profits_losses: ProfitLoss
            :return: ProfitLoss
            """
            for profit_loss in profits_losses:
                profit_loss = profit_loss
                """:type: ProfitLoss"""

                position_set = None
                if profit_loss.underlying:
                    position_set = PositionSet.objects.filter(
                        Q(underlying=profit_loss.underlying) & Q(status='Open')
                    )
                elif profit_loss.future:
                    position_set = PositionSet.objects.filter(
                        Q(future=profit_loss.future) & Q(status='Open')
                    )

                if position_set.exists():
                    profit_loss.position_set = position_set.first()
                    profit_loss.save()

            return profits_losses

    # noinspection PyPep8Naming
    class save(object):
        """
        Get data from filled orders and insert then into db
        """
        context_path = 'position.classes.context'

        def __init__(self, filled_orders):
            self.filled_orders = filled_orders

        def get_underlying_symbols(self):
            """
            Get underlying symbol from filled orders
            :rtype : list
            """
            underlying_symbols = list()
            if self.filled_orders:
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

        def create_set(self, filled_orders):
            """
            Create position context using filled_orders
            :param filled_orders: QuerySet
            :return: PositionSet
            """
            spread = Spread(filled_orders=filled_orders)
            context_module = import_module(
                '%s.%s' % (self.context_path, spread.get_name(module=True, lower=True))
            )
            class_name = 'Context%s' % spread.get_spread_module()
            class_obj = getattr(context_module, class_name)

            filled_order = filled_orders[0]
            """:type: FilledOrder"""

            underlying = filled_order.underlying
            future = filled_order.future
            forex = filled_order.forex

            context = class_obj(
                filled_orders=filled_orders
            ).create_context()

            position_set = PositionSet(
                underlying=underlying,
                future=future,
                forex=forex,
                name=spread.get_name(),
                spread=spread.get_spread()
            )

            # context or contexts
            if type(context) is PositionContext:
                position_set.context = context
            elif type(context) is PositionContexts:
                position_set.contexts = context

            position_set.save()

            return position_set

        def save_underlying_position_set(self):
            """
            Save underlying position set into db
            :rtype : list of PositionSet
            """
            position_sets = list()
            underlying_symbols = self.get_underlying_symbols()

            for symbol in underlying_symbols:
                filled_orders = self.filled_orders.filter(
                    Q(underlying__symbol=symbol) & Q(pos_effect='TO OPEN')
                )
                """:type: QuerySet"""

                if filled_orders.exists():
                    position_sets.append(
                        self.create_set(filled_orders=filled_orders)
                    )

            return position_sets

        def save_future_position_set(self):
            """
            Save future position set into db
            :rtype : list of PositionSet
            """
            position_sets = list()

            future_symbols = self.get_future_symbols()

            for symbol in future_symbols:
                filled_orders = self.filled_orders.filter(
                    Q(future__symbol=symbol) & Q(pos_effect='TO OPEN')
                )
                """:type: QuerySet"""

                if filled_orders.exists():
                    position_sets.append(
                        self.create_set(filled_orders=filled_orders)
                    )

            return position_sets

        def save_forex_position_set(self):
            """
            Save forex position set into db
            :rtype : list of PositionSet
            """
            position_sets = list()
            forex_symbols = self.get_forex_symbols()

            for symbol in forex_symbols:
                filled_orders = self.filled_orders.filter(
                    Q(forex__symbol=symbol) & Q(pos_effect='TO OPEN')
                )
                """:type: QuerySet"""

                if filled_orders.exists():
                    position_sets.append(
                        self.create_set(filled_orders=filled_orders)
                    )

            return position_sets

        def start(self):
            """
            Save underlying, future, forex position set into db
            :rtype : list of PositionSet
            """
            # underlying set
            underlying_position_sets = self.save_underlying_position_set()

            # future set
            future_position_sets = self.save_future_position_set()

            # forex set
            forex_position_sets = self.save_forex_position_set()

            # return reference
            return (
                underlying_position_sets + future_position_sets + forex_position_sets
            )
























