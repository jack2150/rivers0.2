from glob import glob
import locale
import os
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render
from pandas.io.data import get_data_google, get_data_yahoo
from data.classes import OpenThinkBack
from data.holidays import is_not_holiday
from data.offdays import is_not_offdays
from data.models import Stock, OptionContract, Option
from pandas import bdate_range
from rivers.settings import BASE_DIR

locale.setlocale(locale.LC_ALL, '')
THINKBACK_DIR = os.path.join(BASE_DIR, 'data/csv/')
SKIP_DATES = ['2014-02-28']


def data_select_symbol_view(request):
    """
    Select symbol so it import all inside csv folder
    :param request: request
    :return: render
    """
    template = 'data/index.html'

    symbols = [
        os.path.basename(path).upper() for path in
        glob(os.path.join(THINKBACK_DIR, '*'))
        if os.path.isdir(path) and '_daily' not in path
    ]

    parameters = dict(
        symbols=symbols
    )

    return render(request, template, parameters)


def data_symbol_stat_view(request, symbol):
    """
    Get symbol stats detail from db
    :param request: request
    :param symbol: str
    :return: render
    """
    symbol = symbol.upper()
    template = 'data/stats.html'

    try:
        tos_thinkback_stocks = Stock.objects.filter(Q(symbol=symbol) & Q(source='tos_thinkback')).count()
        google_stocks = Stock.objects.filter(Q(symbol=symbol) & Q(source='google')).count()
        yahoo_stocks = Stock.objects.filter(Q(symbol=symbol) & Q(source='yahoo')).count()
        start_date = Stock.objects.filter(symbol=symbol).order_by('date').first().date
        stop_date = Stock.objects.filter(symbol=symbol).order_by('date').last().date
        option_contracts = OptionContract.objects.filter(symbol=symbol).count()
        options = Option.objects.filter(option_contract__symbol=symbol).count()
    except AttributeError:
        tos_thinkback_stocks = 0
        google_stocks = 0
        yahoo_stocks = 0
        start_date = ''
        stop_date = ''
        option_contracts = 0
        options = 0

    parameters = dict(
        symbol=symbol,
        tos_thinkback_stocks=tos_thinkback_stocks,
        google_stocks=google_stocks,
        yahoo_stocks=yahoo_stocks,
        start_date=start_date,
        stop_date=stop_date,
        option_contracts=option_contracts,
        options=options
    )

    return render(request, template, parameters)


def data_tos_thinkback_import_view(request, symbol):
    """
    Import a symbol folder into db
    :param request: request
    :param symbol: str
    :return: render
    """
    template = 'data/run_csv.html'

    symbol = symbol.upper()
    """:type: str"""

    insert_files = list()

    # move files into year folder
    no_year_files = glob(os.path.join(THINKBACK_DIR, symbol, '*.csv'))
    years = sorted(list(set([
        os.path.basename(f)[:4] for f in no_year_files
    ])))

    for year in years:
        year_dir = os.path.join(THINKBACK_DIR, symbol, year)

        # make dir if not exists
        if not os.path.isdir(year_dir):
            os.mkdir(year_dir)

        # move all year files into dir
        for no_year_file in no_year_files:
            #print os.path.basename(no_year_file)[:4], year
            filename = os.path.basename(no_year_file)
            if filename[:4] == year:
                #print 'move ', no_year_file, ' -> ', year_dir
                os.rename(no_year_file, os.path.join(year_dir, filename))

    # get all files in year folder
    files = []
    for year in glob(os.path.join(THINKBACK_DIR, symbol, '*')):
        for csv in glob(os.path.join(year, '*.csv')):
            files.append(csv)

    # stocks = list()
    for csv in files:
        inserted_file = dict(
            path='',
            stock=None,
            contracts=0,
            options=0
        )

        # get date and symbol
        date, symbol = os.path.basename(csv)[:-4].split('-StockAndOptionQuoteFor')

        # insert stock if not exists in db
        query = Q(symbol=symbol) & Q(date=date) & Q(source='tos_thinkback')
        if not Stock.objects.filter(query).exists() and date not in SKIP_DATES:
            # output to console
            print 'running %s file...' % os.path.basename(csv)

            stock_data, option_data = OpenThinkBack(date=date, data=open(csv).read()).format()

            # for view only
            inserted_file['path'] = os.path.basename(csv)

            stock = Stock()
            stock.symbol = symbol
            stock.source = 'tos_thinkback'
            stock.data = stock_data
            stock.save()
            # stocks.append(stock)

            # for view only
            inserted_file['stock'] = stock

            option_codes = [contract['option_code'] for contract, _ in option_data]

            size = 100
            exists_option_codes = list()
            for chunk in [option_codes[i:i + size] for i in range(0, len(option_codes), size)]:
                exists_option_codes += [x[0] for x in OptionContract.objects.filter(
                    option_code__in=chunk).values_list('option_code')]

            new_option_codes = set(option_codes) - set(exists_option_codes)

            contracts = list()
            for option_code in set(option_codes):
                if option_code in new_option_codes:
                    try:
                        contract_dict = [
                            c for c, _ in option_data if c['option_code'] == option_code
                        ][0]
                    except IndexError:
                        print option_code
                        raise Exception()

                    contract = OptionContract()
                    contract.symbol = symbol
                    contract.source = 'tos_thinkback'
                    contract.data = contract_dict
                    contracts.append(contract)

            # insert option contract
            OptionContract.objects.bulk_create(contracts)

            # for view only
            inserted_file['contracts'] = len(contracts)

            option_contracts = list()
            for chunk in [option_codes[i:i + size] for i in range(0, len(option_codes), size)]:
                option_contracts += [
                    option_contract for option_contract in
                    OptionContract.objects.filter(option_code__in=chunk)
                ]

            options = list()
            for contract_dict, option_dict in option_data:
                try:
                    option_contract = [
                        option_contract for option_contract in option_contracts
                        if option_contract.option_code == contract_dict['option_code']
                    ][0]
                except IndexError:
                    raise IndexError('Contract not inserted...')

                option = Option()
                option.option_contract = option_contract
                option.data = option_dict

                options.append(option)

            # insert options
            Option.objects.bulk_create(options)

            # for view only
            inserted_file['options'] = len(options)

            # add into inserted
            insert_files.append(inserted_file)

    # missing files between dates
    missing_files = list()
    if Stock.objects.count() > 2 and Stock.objects.filter(symbol=symbol).exists():
        bdays = bdate_range(
            start=Stock.objects.filter(symbol=symbol).order_by('date').first().date,
            end=Stock.objects.filter(symbol=symbol).order_by('date').last().date,
            freq='B'
        )

        for bday in bdays:
            try:
                Stock.objects.get(
                    Q(symbol=symbol) & Q(source='tos_thinkback') &
                    Q(date=bday.strftime('%Y-%m-%d'))
                )
            except ObjectDoesNotExist:
                if is_not_holiday(bday.strftime('%Y-%m-%d')) and \
                        is_not_offdays(bday.strftime('%m/%d/%y')):
                    missing_files.append(
                        dict(
                            filename='%s-StockAndOptionQuoteFor%s.csv' % (
                                bday.strftime('%Y-%m-%d'), symbol
                            ),
                            date=bday.strftime('%m/%d/%y')
                        )

                    )

    parameters = dict(
        symbol=symbol,
        insert_files=insert_files,
        missing_files=missing_files
    )

    return render(request, template, parameters)


def data_web_import_view(request, symbol=''):
    """
    Select symbol for web get google data
    :param symbol: str
    :param request: request
    :return: render
    """
    # noinspection PyShadowingNames
    def create_stock(symbol, index, data, source):
        """
        Create a stock object
        :param symbol: str
        :param index: datetime
        :param data: dict
        :param source: str
        :return: Stock
        """
        return Stock(
            symbol=symbol,
            date=index.strftime('%Y-%m-%d'),
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            volume=data['Volume'],
            source=source
        )

    template = 'data/run_web.html'

    if symbol:
        symbol = symbol.upper()
        stocks = Stock.objects.filter(symbol=symbol)

        if stocks.exists():
            tos_thinkback = stocks.filter(source='tos_thinkback').order_by('date')

            if tos_thinkback.exists() and tos_thinkback.count() > 1:
                tb_first_date = tos_thinkback.first().date
                tb_last_date = tos_thinkback.last().date
            else:
                raise LookupError(
                    '< {symbol} > No enough stock data from source tos_thinkback.'.format(
                        symbol=symbol
                    )
                )

            web_stocks = stocks.filter(Q(source='google') | Q(source='yahoo')).order_by('date')
            new_stocks = list()

            if web_stocks.exists():
                # generate a list of date then web get
                # tos_thinkback_dates = [stock.date for stock in tos_thinkback]

                #print tos_thinkback_dates
                # generate a list of bday using tb date, remove date from list using google date
                google_dates = [stock.date.strftime('%Y-%m-%d') for stock
                                in web_stocks.filter(source='google')]

                yahoo_dates = [stock.date.strftime('%Y-%m-%d') for stock
                               in web_stocks.filter(source='yahoo')]

                google_data = get_data_google(
                    symbols=symbol,
                    #start='2015-04-01', end='2015-04-10',  # test only
                    start=tb_first_date, end=tb_last_date,
                    adjust_price=True
                )

                for index, data in google_data.iterrows():
                    if index.strftime('%Y-%m-%d') not in google_dates:
                        # not found for google, insert db
                        if int(data['Volume']) > 0:
                            stock = create_stock(symbol, index, data, 'google')
                            new_stocks.append(stock)

                yahoo_data = get_data_yahoo(
                    symbols=symbol,
                    # start='2015-04-01', end='2015-04-10',  # test only
                    start=tb_first_date, end=tb_last_date,
                    adjust_price=True
                )

                for index, data in yahoo_data.iterrows():
                    if index.strftime('%Y-%m-%d') not in yahoo_dates:
                        # not found for google, insert db
                        if int(data['Volume']) > 0:
                            stock = create_stock(symbol, index, data, 'yahoo')
                            new_stocks.append(stock)

            else:
                # import all data, google
                google_data = get_data_google(
                    symbols=symbol,
                    # start='2015-04-01', end='2015-04-10',  # test only
                    start=tb_first_date, end=tb_last_date,
                    adjust_price=True
                )

                for index, data in google_data.iterrows():
                    if int(data['Volume']) > 0:
                        stock = create_stock(symbol, index, data, 'google')
                        new_stocks.append(stock)

                    #print index, data['Open'], data['High'], data['Low'], data['Close'], data['Volume']

                # import all data, yahoo
                yahoo_data = get_data_yahoo(
                    symbols=symbol,
                    # start='2015-04-01', end='2015-04-10',  # test only
                    start=tb_first_date, end=tb_last_date,
                    adjust_price=True
                )

                for index, data in yahoo_data.iterrows():
                    if int(data['Volume']) > 0:
                        stock = create_stock(symbol, index, data, 'yahoo')
                        new_stocks.append(stock)

            # bulk insert
            if len(new_stocks):
                Stock.objects.bulk_create(new_stocks)

        else:
            raise ObjectDoesNotExist(
                "No stock data on < {symbol} >, run tos_thinkback before get google".format(
                    symbol=symbol
                )
            )
    else:
        raise ValueError('Symbol is blank.')

    # reset
    # Stock.objects.filter(symbol=symbol).filter(source='google').delete()

    parameters = dict(
        symbol=symbol,
        stocks=new_stocks
    )

    return render(request, template, parameters)


def data_daily_import_view(request):
    """
    Import all csv files in daily folder
    then insert web data for that date
    :param request: request
    :return: render
    """
    template = 'data/daily.html'

    insert_files = list()

    files = [
        path for path in
        glob(os.path.join(THINKBACK_DIR, '_daily', '*.csv'))
    ]

    for f in files:
        contracts = 0
        options = 0

        # get filename and dir
        filename = os.path.basename(f)
        print 'running file: %s...' % filename
        date, symbol = map(
            lambda x: x.upper(),
            filename[:-4].split('-StockAndOptionQuoteFor')
        )

        # file into dict
        stock_data, option_data = OpenThinkBack(date=date, data=open(f).read()).format()

        # save stock
        stock = Stock()
        stock.symbol = symbol
        stock.source = 'tos_thinkback'
        stock.data = stock_data
        stock.save()

        # save contract and option
        for contract_dict, option_dict in option_data:
            try:
                contract = OptionContract.objects.get(option_code=contract_dict['option_code'])
            except ObjectDoesNotExist:
                contract = OptionContract()
                contract.symbol = symbol
                contract.source = 'tos_thinkback'
                contract.data = contract_dict
                contract.save()
                contracts += 1

            option = Option()
            option.option_contract = contract
            option.data = option_dict
            option.save()
            options += 1

        # move file into folder
        year = filename[:4]
        year_dir = os.path.join(THINKBACK_DIR, symbol, year)

        # make dir if not exists
        if not os.path.isdir(year_dir):
            os.mkdir(year_dir)

        os.rename(f, os.path.join(year_dir, os.path.basename(f)))

        # save data from web
        google_data = get_data_google(
            symbols=symbol,
            # start='2015-04-01', end='2015-04-10',  # test only
            start=date, end=date,
            adjust_price=True
        )

        yahoo_data = get_data_yahoo(
            symbols=symbol,
            # start='2015-04-01', end='2015-04-10',  # test only
            start=date, end=date,
            adjust_price=True
        )

        for index, data in google_data.iterrows():
            if int(data['Volume']) > 0:
                google_stock = Stock(
                    symbol=symbol,
                    date=index.strftime('%Y-%m-%d'),
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    volume=data['Volume'],
                    source='google'
                )
                google_stock.save()

        for index, data in yahoo_data.iterrows():
            if int(data['Volume']) > 0:
                yahoo_stock = Stock(
                    symbol=symbol,
                    date=index.strftime('%Y-%m-%d'),
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    volume=data['Volume'],
                    source='yahoo'
                )
                yahoo_stock.save()

        insert_files.append(
            dict(
                symbol=symbol,
                date=date,
                path=filename,
                stock=1,
                contracts=contracts,
                options=options
            )
        )

    parameters = dict(
        insert_files=insert_files
    )

    return render(request, template, parameters)