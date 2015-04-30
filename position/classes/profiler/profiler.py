from datetime import datetime
from django.db.models import Q
from pandas import bdate_range
from pandas.tseries.offsets import BDay, Day
from data.holidays import is_holiday
from data.models import Stock
from data.offdays import is_offdays
from position.models import PositionSet


class Profiler(object):
    def __init__(self, position_set, date=None):
        """
        :param position_set: PositionSet
        :param date: datetime or str
        """
        self.position_set = position_set
        """:type: PositionSet"""

        self.filled_orders = position_set.filledorder_set \
            .filter(Q(trade_summary__date__lte=date) if date else Q()) \
            .order_by('trade_summary__date')
        """:type: FilledOrder"""

        self.position_instruments = position_set.positioninstrument_set \
            .filter(Q(position_summary__date__lte=date) if date else Q()) \
            .order_by('position_summary__date')
        """:type: PositionInstruments"""

        if date is None:
            if self.position_set.stop_date:
                self.date = self.position_set.stop_date
            else:
                self.date = datetime.today().date()
        else:
            self.date = datetime.strptime(date, '%Y-%m-%d').date()

        self.start_date = self.position_set.start_date
        self.stop_date = self.position_set.stop_date if self.position_set.stop_date else datetime.today()

        self.stocks = None
        """:type: QuerySet"""

    @staticmethod
    def move_bday(date, day):
        """
        Return next bday which it is not holidays or offdays
        :param date: str or datetime
        :param day: int (positive or negative)
        :return: datetime
        """
        if type(date) == str:
            date = datetime.strptime(date, '%Y-%m-%d')

        next_bday = date + BDay(day)
        # check it is not holiday
        while is_holiday(date=next_bday.strftime('%Y-%m-%d')) \
                or is_offdays(date=next_bday.strftime('%m/%d/%y')):
            day += 1 if day > 0 else -1
            next_bday = date + BDay(day)

        return next_bday.to_datetime()

    def create_opinion_button(self):
        """
        Create opinion button parameters
        :return: dict
        """
        try:
            # opinion saved
            if self.date == self.position_set.stop_date and self.position_set.status == 'CLOSE':
                opinion_button = self.position_set.positionopinion_set.order_by('date')
                if opinion_button.exists():
                    opinion_button = dict(
                        object=opinion_button.last(),
                        saved=True
                    )
                else:
                    opinion_button = dict(saved=False)
            else:
                bday = self.move_bday(self.date, 1)
                opinion_button = self.position_set.positionopinion_set \
                    .filter(date__lte=bday).order_by('date').last()

                if bday.strftime('%Y-%m-%d') == opinion_button.date.strftime('%Y-%m-%d'):
                    opinion_button = dict(
                        object=opinion_button,
                        saved=True,
                    )
                else:
                    opinion_button = dict(saved=False)

        except AttributeError:
            opinion_button = dict(saved=False)

        return opinion_button

    def create_position_opinions(self):
        """

        :return: PositionOpinion
        """
        # position opinions
        position_opinions = self.position_set.positionopinion_set.filter(
            date__lte=self.date
        ).order_by('date')

        bull = dict(count=0, count_pct=0.0, correct=0, correct_pct=0.0, wrong=0, wrong_pct=0.0)
        bear = dict(count=0, count_pct=0.0, correct=0, correct_pct=0.0, wrong=0, wrong_pct=0.0)
        for count, opinion in enumerate(position_opinions, start=1):
            if opinion.direction == 'BULL':
                bull['count'] += 1
                if opinion.direction_result:
                    bull['correct'] += 1
                else:
                    bull['wrong'] += 1
                bull['count_pct'] = round(bull['count'] / float(count) * 100, 2)
                bull['correct_pct'] = round(bull['correct'] / float(bull['count']) * 100, 2)
                bull['wrong_pct'] = round(bull['wrong'] / float(bull['count']) * 100, 2)

            elif opinion.direction == 'BEAR':
                bear['count'] += 1
                if opinion.direction_result:
                    bear['correct'] += 1
                else:
                    bear['wrong'] += 1
                bear['count_pct'] = round(bear['count'] / float(count) * 100, 2)
                bear['correct_pct'] = round(bear['correct'] / float(bear['count']) * 100, 2)
                bear['wrong_pct'] = round(bear['wrong'] / float(bear['count']) * 100, 2)

            # assign dict
            opinion.bull = bull.copy()
            opinion.bear = bear.copy()

        return position_opinions

    def create_position_dates(self):
        """
        Create position date related values
        :return: dict
        """
        # get dates
        dte = 0
        expire_date = ''
        if not any([x in self.position_set.spread for x in ('CALENDAR', 'DIAGONAL')]):
            try:
                position_options = self.position_instruments.last().positionoption_set

                if position_options.exists():
                    dte = self.position_instruments.last().positionoption_set.last().days + 1
                    dte = dte if dte > 0 else 0  # reset if already expired

                    expire_date = datetime.strptime((self.stop_date + Day(dte)).strftime('%Y-%m-%d'), '%Y-%m-%d').date()
            except AttributeError:
                dte = 0
                expire_date = None

        if self.start_date != self.stop_date:
            pass_bdays = len(bdate_range(start=self.start_date, end=self.date))
            pass_days = (self.date - self.start_date).days + 1
        else:
            pass_bdays = len(bdate_range(start=self.start_date, end=datetime.today()))
            pass_days = (datetime.today().date() - self.start_date).days + 1

        return dict(
            pass_bdays=pass_bdays,
            pass_days=pass_days,
            start_date=self.start_date,
            stop_date=self.stop_date if self.stop_date == self.date else self.date,
            dte=dte,
            expire_date=expire_date,
        )

    def create_historical_positions(self):
        """
        Create historical position sets
        :return: QuerySet
        """
        return PositionSet.objects.filter(
            Q(underlying__symbol=self.position_set.underlying.symbol)
        ).exclude(id=self.position_set.id)

    def set_stocks(self):
        """
        Get stock records from quote db
        """
        if self.position_set.underlying:
            dates = [i.position_summary.date for i in self.position_instruments] + \
                    [self.move_bday(self.start_date, -1)]
            # get stocks data
            self.stocks = Stock.objects.filter(
                Q(symbol=self.position_set.underlying.symbol) &
                Q(date__in=dates) &
                Q(source='google')
            ).order_by('date')
        else:
            raise LookupError('Missing underlying object when get stock records.')



























