import pandas as pd
import os
import time
from datetime import datetime

path = '/Users/marcel/workspace/data/intraQuarter'

def Key_Stats(gather="Total Debt/Equity (mrq)"):
    statspath = path+'/_KeyStats'
    stock_list = [x[0] for x in os.walk(statspath)]
    df = pd.DataFrame(columns=['Date',
                               'Unit',
                               'Ticker',
                               'DE Ratio',
                               'Price',
                               'stock_p_change',
                               'SP500',
                               'sp500_p_change'])
    sp500_df = pd.DataFrame.from_csv("YAHOO-INDEX_GSPC.csv")

    ticker_list = []

    for each_dir in stock_list[1:]:
        each_file = os.listdir(each_dir)
        ticker =each_dir.split("_KeyStats/")[1]
        ticker_list.append(ticker)

        starting_stock = False
        starting_sp500 = False

        if len(each_file) > 0:
            for file in each_file:

                date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
                unix_time = time.mktime(date_stamp.timetuple())
                full_file_path = each_dir+'/'+file
                source = open(full_file_path,'r').read()
                try:
                    # DE Ratio
                    value = source.split(gather+':</td><td class="yfnc_tabledata1">')[1].split('</td>')[0]
                    try:
                        sp500_date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d')
                        row = sp500_df[(sp500_df.index == sp500_date)]
                        sp500_value = float(row["Adjusted Close"])
                    except:
                        try:
                            sp500_date = datetime.utcfromtimestamp(unix_time-259200).strftime('%Y-%m-%d')
                            row = sp500_df[(sp500_df.index == sp500_date)]
                            sp500_value = row["Adjusted Close"]
                            sp500_value = float(sp500_value)
                        except:
                            pass
                    # stock price
                    try:
                        stock_price = source.split('</small><big><b>')[1].split('</b></big>')[0]
                        stock_price = float(stock_price)
                    except:

                        try:
                            stock_price = source.split('<span id="yfs_l10_' + ticker + '">')[1].split('</span>')[0]
                            stock_price = float(stock_price)
                        except:

                            try:
                                stock_price = source.split('<span id="yfs_l84_' + ticker + '">')[1].split('</span>')[0]
                                stock_price = float(stock_price)
                            except:
                                pass

                    # print("stock_price:", stock_price, "ticker:", ticker)

                    if not starting_stock:
                        starting_stock_value = stock_price
                        starting_stock = True
                    if not starting_sp500:
                        starting_sp500_value = sp500_value
                        starting_sp500 = True

                    stock_p_change = (stock_price - starting_stock_value)/starting_stock_value*100.0
                    sp500_p_change = (sp500_value - starting_sp500_value)/starting_sp500_value*100.0

                    df = df.append({'Date': date_stamp,
                                    'Unix': unix_time,
                                    'Ticker': ticker,
                                    'DE Ratio': value,
                                    'Price': stock_price,
                                    'stock_p_change': stock_p_change,
                                    'SP500': sp500_value,
                                    'sp500_p_change': sp500_p_change
                                    },

                                   ignore_index=True)
                except IndexError:
                    # print 'filename: %s' %full_file_path
                    # print 'Warning cannot find %s for ticker %s.\n ' % (gather, ticker)
                    pass

    save = gather.replace(' ','').replace(')','').replace('(','').replace('/','') + '.csv'
    print save
    df.to_csv(save)

Key_Stats()