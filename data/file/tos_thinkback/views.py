from glob import glob
import os
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q
from django.shortcuts import render
from data.file.tos_thinkback.classes import OpenThinkBack
from data.file.tos_thinkback.csv import THINKBACK_DIR
from data.file.tos_thinkback.holidays import is_not_holiday
from data.file.tos_thinkback.offdays import is_not_offdays
from data.models import Stock, OptionContract, Option
import pandas as pd
from tos_import.models import Underlying


def tos_thinkback_import_select_view(request):
    """
    Select symbol so it import all inside csv folder
    :param request: request
    :return: render
    """
    template = 'tos_thinkback/index.html'

    symbols = [
        os.path.basename(path).upper() for path in
        glob(os.path.join(THINKBACK_DIR, '*'))
        if os.path.isdir(path)
    ]

    parameters = dict(
        symbols=symbols
    )

    return render(request, template, parameters)


def tos_thinkback_import_run_view(request, symbol):
    """
    Import a symbol folder into db
    :param request: request
    :param symbol: str
    :return: render
    """
    template = 'tos_thinkback/run.html'

    symbol = symbol.upper()
    """:type: str"""

    insert_files = list()

    # get all files in year folder
    files = []
    for year in glob(os.path.join(THINKBACK_DIR, symbol, '*')):
        for csv in glob(os.path.join(year, '*.csv')):
            files.append(csv)

    #stocks = list()
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
        if not Stock.objects.filter(Q(symbol=symbol) & Q(date=date)).exists():
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
            #stocks.append(stock)

            # for view only
            inserted_file['stock'] = stock

            """
            # insert option contract and options
            options = list()
            for contract_dict, option_dict in option_data:
                try:
                    option_contract = OptionContract.objects.get(
                        option_code=contract_dict['option_code']
                    )
                except ObjectDoesNotExist:
                    option_contract = OptionContract()
                    option_contract.underlying = underlying
                    option_contract.data = contract_dict
                    option_contract.save()

                option = Option()
                option.option_contract = option_contract
                option.data = option_dict

                options.append(
                    option
                )

            Option.objects.bulk_create(options)

            # save options

            Option.objects.bulk_create(options)
            """

            option_codes = [contract['option_code'] for contract, _ in option_data]
            #exists_option_codes = [x[0] for x in OptionContract.objects.filter(
            #    option_code__in=option_codes
            #).values_list('option_code')]

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

            #option_contracts = [
            #    option_contract for option_contract in
            #    OptionContract.objects.filter(option_code__in=option_codes)
            #]

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

    # insert stock
    #Stock.objects.bulk_create(stocks)

    # missing files between dates
    missing_files = list()
    if Stock.objects.count() > 2:
        bdays = pd.bdate_range(
            start=Stock.objects.filter(symbol=symbol).order_by('date').first().date,
            end=Stock.objects.filter(symbol=symbol).order_by('date').last().date,
            freq='B'
        )

        for bday in bdays:
            try:
                Stock.objects.get(
                    Q(symbol=symbol) &
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

    # reset all
    #Stock.objects.all().delete()
    #OptionContract.objects.all().delete()
    #Option.objects.all().delete()

    parameters = dict(
        insert_files=insert_files,
        missing_files=missing_files
    )

    return render(request, template, parameters)