from django.core.exceptions import ObjectDoesNotExist
from pandas.tseries.offsets import Hour, Minute
from position.classes.profiler.profiler import Profiler


class ProfilerLongStock(Profiler):
    def __init__(self, position_set, date=''):
        """
        :param position_set: PositionSet
        :param date: datetime
        """
        Profiler.__init__(self, position_set, date)

        self.set_stocks()

        self.open_order = self.filled_orders.get(pos_effect='TO OPEN')
        """:type: FilledOrder"""

        try:
            self.close_order = self.filled_orders.get(pos_effect='TO CLOSE')
            """:type: FilledOrder"""
        except ObjectDoesNotExist:
            self.close_order = None

    def create_position_info(self):
        """
        Create daily profit loss using stock data not using statement data
        :return: dict
        """
        last_close = self.stocks.last().close
        if self.date == self.position_set.stop_date and self.position_set.status == 'CLOSE':
            last_close = self.close_order.net_price

        stage = self.position_set.get_stage(last_close)
        status = self.position_set.current_status(
            new_price=last_close, old_price=self.stocks.reverse()[1].close
        )

        pl_open = (last_close - self.open_order.net_price) * self.open_order.quantity
        pl_open_pct = round(pl_open / (self.open_order.net_price * self.open_order.quantity) * 100, 2)

        if self.date == self.start_date:
            pl_day = (last_close - self.open_order.net_price) * self.open_order.quantity
        elif self.date == self.stop_date:
            pl_day = (self.close_order.net_price - self.stocks.reverse()[1].close) * self.open_order.quantity
        else:
            pl_day = (last_close - self.stocks.reverse()[1].close) * self.open_order.quantity
        pl_day_pct = round(pl_day / (self.open_order.net_price * self.open_order.quantity) * 100, 2)

        return dict(
            stage_id=stage.id,
            stage=stage.stage_name,
            status=status,
            pl_open=round(pl_open, 2),
            pl_open_pct=pl_open_pct,
            pl_day=round(pl_day, 2),
            pl_day_pct=pl_day_pct,
            enter_price=self.open_order.net_price,
            exit_price=self.close_order.net_price if self.close_order else 0.0,
            quantity=self.open_order.quantity,
            holding=self.open_order.net_price * self.open_order.quantity,
            bp_effect=self.position_instruments.last().bp_effect,
            date=(self.date + Hour(17) + Minute(30)).to_datetime().date(),
        )

    def create_position_stocks(self):
        """
        Create profit loss
        :return:
        """
        position_stocks = list()

        p_open_count = 0
        l_open_count = 0
        p_day_count = 0
        l_day_count = 0

        for key, (stock0, stock1) in enumerate(zip(self.stocks[:len(self.stocks) - 1], self.stocks[1:]), start=1):
            net_change = stock1.close - stock0.close
            pct_change = round((stock1.close - stock0.close) / stock0.close * 100, 2)

            if stock1.date == self.position_set.stop_date and self.position_set.status in ['CLOSE', 'EXPIRE']:
                stage = self.position_set.status
                status = 'UNKNOWN'
            else:
                stage = self.position_set.get_stage(price=stock1.close).stage_name
                status = self.position_set.current_status(
                    old_price=stock0.close, new_price=stock1.close
                )

            pl_open = (stock1.close - self.open_order.net_price) * self.open_order.quantity
            pl_open_pct = round((pl_open / (self.open_order.net_price * self.open_order.quantity)) * 100, 2)

            if key == 1:
                pl_day = (stock1.close - self.open_order.net_price) * self.open_order.quantity
                pl_day_pct = round((pl_day / (self.open_order.net_price * self.open_order.quantity)) * 100, 2)
            else:
                pl_day = (stock1.close - stock0.close) * self.open_order.quantity
                pl_day_pct = round((pl_day / (self.open_order.net_price * self.open_order.quantity)) * 100, 2)

            if pl_open > 0:
                p_open_count += 1
            elif pl_open < 0:
                l_open_count += 1

            p_open_pct = p_open_count / float(key) * 100
            l_open_pct = l_open_count / float(key) * 100

            if pl_day > 0:
                p_day_count += 1
            elif pl_day < 0:
                l_day_count += 1

            p_day_pct = p_day_count / float(key) * 100
            l_day_pct = l_day_count / float(key) * 100

            position_stocks.append(
                dict(
                    date=stock1.date,
                    open=stock1.open,
                    high=stock1.high,
                    low=stock1.low,
                    close=stock1.close,
                    net_change=net_change,
                    pct_change=pct_change,
                    pl_open=float(pl_open),
                    pl_open_pct=pl_open_pct,
                    p_open_count=p_open_count,
                    p_open_pct=p_open_pct,
                    l_open_count=l_open_count,
                    l_open_pct=l_open_pct,
                    p_day_count=p_day_count,
                    p_day_pct=p_day_pct,
                    l_day_count=l_day_count,
                    l_day_pct=l_day_pct,
                    pl_day=float(pl_day),
                    pl_day_pct=pl_day_pct,
                    stage=stage,
                    status=status,
                )
            )

        return position_stocks
