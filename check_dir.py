from glob import glob
import os
import pandas as pd
import sys

symbol = sys.argv[1]
year = int(sys.argv[2])
check_folder = r'C:\Users\Jack\Projects\rivers\data\file\tos_thinkback\csv\%s\20%02d' % (symbol, year)

bdays = pd.bdate_range(start='20%02d-01-01' % year, end='20%02d-12-31' % year, freq='B')

print bdays

dates = []
print '.' * 60
print 'check weekend files:'
for csv_file in glob(os.path.join(check_folder, '*.*')):
    filename = os.path.basename(csv_file)
    date, symbol = filename[:-4].split('-StockAndOptionQuoteFor')
    # print date, symbol
    dates.append(date)

    if date not in bdays:
        print date, 'weekend...'
        os.remove(csv_file)
        print 'file removed...'
else:
    print 'done!'
    print '.' * 60

print '.' * 60
print 'check missing files:'
for bday in bdays:
    if bday.strftime('%Y-%m-%d') not in dates:
        print bday.strftime('%m/%d/%y'), 'missing...'
else:
    print 'done!'
    print '.' * 60
