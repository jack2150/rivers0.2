from django.db.models import Q
from position.models import PositionSet


class PositionSetController(object):
    """
    usage after all import:
    pos_set_controller = PositionSetController(filled_orders)
    pos_set_controller.create_position_sets()
    pos_set_controller.close_position_sets()
    pos_set_controller.batch_update_foreign_keys()
    """
    def __init__(self, filled_orders):
        """
        :param filled_orders: QuerySet
        """
        self.filled_orders = filled_orders
        """:type: QuerySet"""

        self.position_sets = list()
        self.open_sets = list()
        self.close_sets = list()

        self.open_orders = self.filled_orders.filter(
            pos_effect='TO OPEN'
        ).exclude(Q(order='ROC') | Q(order='RCL') | Q(order='ROP'))  # no forex daily adjust
        self.close_orders = self.filled_orders.filter(
            pos_effect='TO CLOSE'
        ).exclude(Q(order='ROC') | Q(order='RCL') | Q(order='ROP'))  # no forex daily adjust

        # get distinct symbols
        underlying_symbols = [Q(underlying=obj) for obj in self.filled_orders.values_list(
            'underlying', flat=True).distinct() if obj]

        future_symbols = [Q(future=obj) for obj in self.filled_orders.values_list(
            'future', flat=True).distinct() if obj]

        forex_symbols = [Q(forex=obj) for obj in self.filled_orders.values_list(
            'forex', flat=True).distinct() if obj]

        self.queries = underlying_symbols + future_symbols + forex_symbols

    def create_position_sets(self, date=''):
        """
        Take a list of open orders and make a list of position sets
        group open filled orders by using underlying or future or forex
        :return: list of PositionSet
        """
        for query in self.queries:
            filled_orders = self.open_orders.filter(query)

            # save filled order into position set and all foreign keys
            if filled_orders.exists():
                position_set = PositionSet()
                position_set.manager.filled_orders = filled_orders
                position_set.save()
                position_set.manager.update_foreign_keys(date=date)

                self.open_sets.append(position_set)

        return self.open_sets

    def close_position_sets(self, date=''):
        """
        Take a list of close orders and existing position sets status to closed
        also add foreign key for filled orders
        :return: list of PositionSet
        """
        for query in self.queries:
            filled_orders = self.close_orders.filter(query)

            # save filled order into position set and all foreign keys
            if filled_orders.exists():
                position_sets = PositionSet.objects.filter(query).filter(status='OPEN')

                if position_sets.exists():

                    position_set = position_sets.first()
                    """:type: PositionSet"""

                    position_set.manager.filled_orders = filled_orders
                    position_set.manager.update_foreign_keys(date=date)
                    position_set.status = 'CLOSE'
                    position_set.save()

                    self.close_sets.append(position_set)

        return self.close_sets

    def batch_update_foreign_keys(self, date=''):
        """
        Every import, when no trade activity, it still have
        instruments, futures, forexs, profit_loss...
        you get those items and set all foreign keys
        :return:
        """
        self.position_sets = PositionSet.objects.filter(status='OPEN')

        open_ids = [position_set.id for position_set in self.open_sets]
        close_ids = [position_set.id for position_set in self.close_sets]
        ids = open_ids + close_ids

        for position_set in self.position_sets:
            if position_set.id not in ids:
                ref = position_set.manager.update_foreign_keys(date=date)

                if position_set.underlying and not len(ref['position_instruments']):
                    position_set.status = 'EXPIRED'
                    position_set.save()
                elif position_set.future and not len(ref['position_futures']):
                    position_set.status = 'EXPIRED'
                    position_set.save()
                #elif position_set.forex and not len(ref['position_forexs']):
                #    position_set.status = 'EXPIRED'
                #    position_set.save()
