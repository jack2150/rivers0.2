from datetime import datetime
from django.utils.timezone import utc
from app_pms.classes.io.open_csv import OpenCSV


class OpenTA(OpenCSV):
    def __init__(self, data):
        OpenCSV.__init__(self, data)

        self.working_order_keys = [
            '', '', 'time_placed', 'spread', 'side', 'quantity',
            'pos_effect', 'symbol', 'expire_date', 'strike', 'contract',
            'price', 'order', 'tif', 'mark', 'status'
        ]

        self.filled_order_keys = [
            '', 'exec_time', 'spread', 'side', 'quantity', 'pos_effect',
            'symbol', 'expire_date', 'strike', 'contract', 'price',
            'net_price', 'order'
        ]

        self.cancelled_order_keys = [
            '', '', 'time_cancelled', 'spread', 'side', 'quantity',
            'pos_effect', 'symbol', 'expire_date', 'strike', 'contract',
            'price', 'order', 'tif', 'status'
        ]

        self.rolling_strategy_keys = [
            'position', 'new_expire_date', 'call_by', 'days_begin', 'order_price',
            'active_time', 'move_to_market_time', 'status'
        ]

        self.rolling_strategy_options = [
            'side', 'symbol', 'right', 'ex_month', 'ex_year', 'strike_price', 'contract'
        ]

        self.working_order = list()
        self.filled_order = list()
        self.cancelled_order = list()
        self.rolling_strategy = list()

    @classmethod
    def convert_datetime(cls, date):
        """
        Convert date format into YYYY-MM-DD 7/23/14 22:21:27
        :param date: str
        :return: str
        """
        result = datetime.strptime(date, '%m/%d/%y %H:%M:%S').replace(tzinfo=utc)
        # result = timezone(result, timezone.get_current_timezone())

        return result

    @classmethod
    def convert_hour_minute(cls, time):
        """
        Convert date format into %H:%M:%S
        :param time: str
        :return: str
        """
        result = datetime.strptime(time, '%H:%M').strftime('%H:%M:%S')

        return result

    @classmethod
    def convert_type(cls, prop_obj, column_name, specific_type, empty_value):
        """
        Convert item for dict in list into specific type
        :param prop_obj: list
        :param column_name: str
        :param specific_type: type
        :return: None
        """
        for key, item in enumerate(prop_obj):
            if item[column_name]:
                prop_obj[key][column_name] = specific_type(item[column_name])
            else:
                prop_obj[key][column_name] = empty_value

    @classmethod
    def replace_nan(cls, prop_obj):
        """
        Convert item for dict in list into specific type
        :param prop_obj: list
        :return: None
        """
        for key, item in enumerate(prop_obj):
            for column, value in item.items():
                if str(value) == 'nan':
                    prop_obj[key][column] = 0.0

    def remove_working_order_rows(self):
        """
        Remove empty quantity row in working orders
        """
        for key, working_order in enumerate(self.working_order):
            if not working_order['quantity']:
                self.working_order.pop(key)

    def set_working_order(self):
        """
        Set working_order into class property
        :return: None
        """
        self.set_values(
            start_phrase='Working Orders',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.working_order_keys,
            prop_name='working_order'
        )
        self.remove_working_order_rows()
        self.fillna_dict_with_exists(
            self.working_order,
            'time_placed',
            ('time_placed', 'spread', 'order', 'tif', 'mark', 'status')
        )

        self.working_order = map(self.del_empty_keys, self.working_order)
        self.convert_type(self.working_order, 'time_placed', self.convert_datetime, None)
        self.convert_type(self.working_order, 'quantity', int, 0)
        self.convert_type(self.working_order, 'strike', float, 0.0)
        self.convert_type(self.working_order, 'price', float, 0.0)
        self.convert_type(self.working_order, 'expire_date', str, '')

    def set_filled_order(self):
        """
        Set equity into class property
        :return: None
        """
        self.set_values(
            start_phrase='Filled Orders',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.filled_order_keys,
            prop_name='filled_order'
        )

        self.filled_order = map(self.del_empty_keys, self.filled_order)
        self.fillna_dict_with_exists(
            self.filled_order,
            'exec_time',
            ('exec_time', 'spread', 'order')
        )

        self.replace_nan(self.filled_order)
        self.convert_type(self.filled_order, 'exec_time', self.convert_datetime, 0)

        self.convert_type(self.filled_order, 'quantity', int, 0)
        self.convert_type(self.filled_order, 'strike', float, 0.0)
        self.convert_type(self.filled_order, 'price', float, 0.0)
        self.convert_type(self.filled_order, 'net_price', float, 0.0)
        self.convert_type(self.filled_order, 'expire_date', str, '')

    def set_cancelled_order(self):
        """
        Set cancelled_orders into class property
        :return: None
        """
        self.set_values(
            start_phrase='Cancelled Orders',
            end_phrase=None,
            start_with=2,
            end_until=-1,
            prop_keys=self.cancelled_order_keys,
            prop_name='cancelled_order'
        )

        self.cancelled_order = map(self.del_empty_keys, self.cancelled_order)
        self.fillna_dict_with_exists(
            self.cancelled_order,
            'time_cancelled',
            ('time_cancelled', 'spread', 'order', 'tif', 'status')
        )
        self.replace_nan(self.cancelled_order)

        self.convert_type(self.cancelled_order, 'time_cancelled', self.convert_datetime, 0)
        self.convert_type(self.cancelled_order, 'quantity', int, 0)
        self.convert_type(self.cancelled_order, 'strike', float, 0.0)
        self.convert_type(self.cancelled_order, 'price', float, 0.0)
        self.convert_type(self.cancelled_order, 'expire_date', str, '')

    def format_rolling_strategy_market_time(self):
        """
        Format rolling strategy market time into start and end
        :return: None
        """
        for key, items in enumerate(self.rolling_strategy):
            move_to_market_time = items['move_to_market_time'].split(' - ')
            self.rolling_strategy[key]['move_to_market_time_start'] = move_to_market_time[0]
            self.rolling_strategy[key]['move_to_market_time_end'] = move_to_market_time[1]
            del self.rolling_strategy[key]['move_to_market_time']

    def format_rolling_strategy_active_time(self):
        """
        Format rolling strategy active time into start and end
        :return: None
        """
        for key, items in enumerate(self.rolling_strategy):
            active_time = items['active_time'].split(' - ')

            self.rolling_strategy[key]['active_time_start'] = active_time[0]
            self.rolling_strategy[key]['active_time_end'] = active_time[1]
            del self.rolling_strategy[key]['active_time']

    def format_rolling_strategy_options(self):
        """
        Format rolling strategy options into sub pieces
        :return: None
        """
        for key, items in enumerate(self.rolling_strategy):
            option = {k: v for k, v in zip(self.rolling_strategy_options, items['position'].split(' '))}
            self.rolling_strategy[key] = dict(items, **option)
            del self.rolling_strategy[key]['position']

    def set_rolling_strategy(self):
        """
        Set rolling_strategy into class property
        :return: None
        """
        self.set_values(
            start_phrase='Rolling Strategies',
            end_phrase=None,
            start_with=2,
            end_until=None,
            prop_keys=self.rolling_strategy_keys,
            prop_name='rolling_strategy'
        )

        # custom format
        self.format_rolling_strategy_options()
        self.format_rolling_strategy_market_time()
        self.format_rolling_strategy_active_time()

        # format
        self.convert_type(self.rolling_strategy, 'side', int, 0)
        self.convert_type(self.rolling_strategy, 'right', int, 0)
        self.convert_type(self.rolling_strategy, 'ex_year', int, 0)
        self.convert_type(self.rolling_strategy, 'strike_price', float, 0.0)

        # time format
        self.convert_type(self.rolling_strategy, 'active_time_start',
                          self.convert_hour_minute, None)
        self.convert_type(self.rolling_strategy, 'active_time_end',
                          self.convert_hour_minute, None)
        self.convert_type(self.rolling_strategy, 'move_to_market_time_start',
                          self.convert_hour_minute, None)
        self.convert_type(self.rolling_strategy, 'move_to_market_time_end',
                          self.convert_hour_minute, None)

    def read(self):
        """
        Most important method, read file then return data
        :return: dict
        """
        self.set_working_order()
        self.set_filled_order()
        self.set_cancelled_order()
        self.set_rolling_strategy()

        return dict(
            working_order=self.working_order,
            filled_order=self.filled_order,
            cancelled_order=self.cancelled_order,
            rolling_strategy=self.rolling_strategy
        )






# todo: fix bug, datetime field










