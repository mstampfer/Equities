from Quandl import Quandl
import pandas as pd
import os
import time
from datetime import date, timedelta, datetime

path = '/Users/marcel/workspace/data/'
auth_token = open('auth_tok.txt', 'r').read()

def Stock_Prices():
    df = pd.DataFrame()
    statspath = path+'intraQuarter/_KeyStats'
    stock_list = [x[0] for x in os.walk(statspath)]

    for each_dir in stock_list[1:]:
        try:

            ticker = each_dir.split('_KeyStats/')[1]
            print ticker
            name = 'WIKI/' + ticker.upper()
            data = Quandl.get(name, trim_start=datetime.strptime('2000-12-12', '%Y-%m-%d'),
                          trim_end=date.today()-timedelta(1),
                          authtoken=auth_token)
            data[ticker.upper()] = data['Adj. Close']

            df = pd.concat([df, data[ticker.upper()]], axis=1)

        except Exception as e:
            print('Error polling Quandl: ' +str(e))

    df.to_csv('stock_prices.csv')



Stock_Prices()

