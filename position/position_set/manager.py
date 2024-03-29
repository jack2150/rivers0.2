from importlib import import_module
from django.db.models import Q
from position.classes.spread import Spread
from tos_import.statement.statement_account.models import ProfitLoss
from tos_import.statement.statement_position.models import PositionInstrument, PositionFuture, PositionForex

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class PositionSetManager(object):
    """
    set get: position_set.manager.filled_orders = filled_orders
    get data: position_set.manager.get_name()
    update: position_set.manager.update.position_instruments()
    """
    context_path = 'position.classes.context'
    stage_path = 'position.classes.stage'

    def __init__(self, position_set):
        self.position_set = position_set
        """:type: PositionSet"""

        self._filled_orders = list()
        """:type: QuerySet"""

        self.contexts = dict(
            break_evens=list(),
            start_profits=list(),
            start_losses=list(),
            max_profits=list(),
            max_losses=list()
        )

        self.stages = list()

    def set_filled_orders(self, filled_orders):
        """
        Input a filled_orders then process it
        and save it into position_set values
        :param filled_orders: QuerySet FilledOrder
        """
        # set to class property
        self._filled_orders = filled_orders

        # start spread analysis
        spread = Spread(filled_orders=filled_orders)
        spread.get_name()
        spread.get_spread()

        filled_order = self._filled_orders[0]
        """:type: FilledOrder"""

        underlying = filled_order.underlying
        future = filled_order.future
        forex = filled_order.forex

        # primary field
        if self.position_set.name == '':
            self.position_set.name = spread.name

        if self.position_set.spread == '':
            self.position_set.spread = spread.spread

        self.position_set.status = 'OPEN'
        if not self.position_set.start_date:
            self.position_set.start_date = filled_order.trade_summary.date

        self.position_set.underlying = underlying
        self.position_set.future = future
        self.position_set.forex = forex

        # position stages
        if spread.get_spread() != 'CUSTOM':
            stage_module = import_module(
                '%s.%s' % (self.stage_path, spread.get_name(module=True, lower=True))
            )
            class_name = 'Stage%s' % spread.get_spread_module()
            class_obj = getattr(stage_module, class_name)
            self.stages = class_obj(filled_orders=filled_orders).create_stages()

    def get_filled_orders(self):
        """
        Return original filled orders queryset
        :return: QuerySet FilledOrder
        """
        return self._filled_orders

    filled_orders = property(fget=get_filled_orders, fset=set_filled_orders)

    def update_foreign_keys(self, date=''):
        """
        Use current position_set id and update
        FilledOrders, PositionInstruments, PositionFutures,
        PositionForexs, ProfitLoss
        :param date: str
        :return: dict
        """
        position_instruments = list()
        position_futures = list()
        position_forexs = list()
        profits_losses = list()
        profit_loss_query = None

        position_summary_query = Q()
        account_summary_query = Q()
        if date != '':
            position_summary_query = Q(position_summary__date=date)
            account_summary_query = Q(account_summary__date=date)

        if self.position_set.id is None:
            raise ValueError('Invalid position_set id, please save before running update_fk.')

        if self.position_set.status == 'CLOSE':
            raise ValueError('Position_set already closed, please use another position_set.')

        # update filled orders
        for filled_order in self.filled_orders:
            filled_order.position_set = self.position_set
            filled_order.save()

        if self.position_set.underlying:
            # update position instrument and profit loss
            PositionInstrument.objects.filter(
                Q(underlying=self.position_set.underlying) & Q(position_set=None)
            ).filter(position_summary_query).update(position_set=self.position_set)

            position_instruments = PositionInstrument.objects.filter(
                position_set=self.position_set
            ).filter(position_summary_query)

            profit_loss_query = Q(underlying=self.position_set.underlying)

        elif self.position_set.future:
            # update position future and profit loss
            PositionFuture.objects.filter(
                Q(future=self.position_set.future) & Q(position_set=None)
            ).filter(position_summary_query).update(position_set=self.position_set)

            position_futures = PositionFuture.objects.filter(
                position_set=self.position_set
            ).filter(position_summary_query)

            profit_loss_query = Q(future=self.position_set.future)

        elif self.position_set.forex:
            # update position forex
            PositionForex.objects.filter(
                Q(forex=self.position_set.forex) & Q(position_set=None)
            ).filter(position_summary_query).update(position_set=self.position_set)

            position_forexs = PositionForex.objects.filter(
                position_set=self.position_set
            ).filter(position_summary_query)

        if profit_loss_query:
            ProfitLoss.objects.filter(profit_loss_query & Q(position_set=None)).filter(
                account_summary_query).update(position_set=self.position_set)

            profits_losses = ProfitLoss.objects.filter(
                profit_loss_query & Q(position_set=self.position_set)
            ).filter(account_summary_query)

        return dict(
            filled_orders=self.filled_orders,
            position_instruments=position_instruments,
            position_futures=position_futures,
            position_forexs=position_forexs,
            profits_losses=profits_losses,
        )