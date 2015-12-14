import pandas as pd
import os
from datetime import datetime
from time import mktime
from glob import glob
import re

path = '/Users/marcel/workspace/Equities/data/'
attributes = {'DE Ratio': 'Total Debt/Equity',
           'Trailing P/E'                       :'Trailing P/E',
           'Price/Sales'                        :'Price/Sales',
           'Price/Book'                         :'Price/Book',
           'Profit Margin'                      :'Profit Margin',
           'Operating Margin'                   :'Operating Margin',
           'Return on Assets'                   :'Return on Assets',
           'Return on Equity'                   :'Return on Equity',
           'Revenue Per Share'                  :'Revenue Per Share',
           'Market Cap'                         :'Market Cap',
           'Forward P/E'                        :'Forward P/E',
           'PEG Ratio'                          :'PEG Ratio',
           'Enterprise Value'                   :'Enterprise Value',
           'Revenue'                            :'Revenue',
           'Gross Profit'                       :'Gross Profit',
           'EBITDA'                             :'EBITDA',
           'Net Income Avl to Common '          :'Net Income Avl to Common ',
           'Earnings Per Share'                 :'Earnings Per Share|Diluted EPS',
           'Earnings Growth'                    :'Earnings Growth',
           'Revenue Growth'                     :'Revenue Growth',
           'Total Cash'                         :'Total Cash',
           'Total Cash Per Share'               :'Total Cash Per Share',
           'Total Debt'                         :'Total Debt',
           'Current Ratio'                      :'Current Ratio',
           'Book Value Per Share'               :'Book Value Per Share',
           'Operating Cash Flow'                :'From Operations|Operating Cash Flow',
           'Beta'                               :'Beta',
           'Held by Insiders'                   :'Held by Insiders',
           'Held by Institutions'               :'Held by Institutions',
           'Shares Short'                       :'Shares Short',
           'Short Ratio'                        :'Short Ratio',
           'Short % of Float'                   :'Short % of Float'
          }

def getValue(df, attribute, timestamp):
    try:
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        row = df[(df.index == date)]
        value = float(row[attribute])
        return value
    except:
        return None

def Key_Stats():

    features = attributes.values()
    statspath = path + 'Yahoo/intraQuarter/_KeyStats'
    keystats_screen_paths = [x[0] for x in os.walk(statspath)]
    output_df = pd.DataFrame()
    sp500_df = pd.DataFrame.from_csv(path + "Yahoo/YAHOO-INDEX_GSPC.csv")
    stock_df = pd.DataFrame.from_csv(path + "Quandl/stock_prices.csv")
    ticker_list = []

    for each_dir in keystats_screen_paths[1:]:
        keystats_files = glob(os.path.join(each_dir, '[0-9]*'))  # no hidden files
        ticker = each_dir.split("_KeyStats/")[1]
        ticker_list.append(ticker)
        print ticker

        if len(keystats_files) > 0:
            for full_file_path in keystats_files:
                filename = os.path.basename(full_file_path)
                date_stamp = datetime.strptime(filename, '%Y%m%d%H%M%S.html')
                unix_time = mktime(date_stamp.timetuple())
                html_source = open(full_file_path, 'r').read()
                value_dict = {}
                output_dict = {}

                for feature in features:
                    try:
                        regex = '(' + feature + ')' + r'.*?\n?\s*?.*?tabledata1">\n?\r?\s*?(-?(\d{1,3},)?\d{1,8}(\.\d{1,8})?M?B?K?|N/A)\%?\n?\r?\s*?</td>'
                        value = re.search(regex, html_source)
                        value = (value.group(2))

                    except Exception:
                        try:
                            regex = '(' + feature + ')' + r'.*?\n?\t*?\s*?.*?\n?.*?tabledata1">\n?\r?\s*?(-?(\d{1,3},)?\d{1,8}(\.\d{1,8})?M?B?|N/A)\%?\n?\r?\s*?</td>'
                            value = re.search(regex, html_source)
                            value = (value.group(2))
                        except:
                            print 'Warning cannot find %s for ticker %s in file %s. ' % (feature, ticker, filename)
                            value = "N/A"

                    value_dict[feature] = value

                    if ',' in str(value):
                        value = value.replace(',', '')

                    if "B" in value:
                        value = float(value.replace("B", '')) * 1000000000.

                    elif "M" in value:
                        value = float(value.replace("M", '')) * 1000000.

                    elif "K" in value:
                        value = float(value.replace("K", '')) * 1000.

                        value_dict[feature] = value

                one_year_later = int(unix_time + 31536000)
                stock_price, sp500_value, stock_1y_value, sp500_1y_value = None, None, None, None

                unix_day = 60 * 60 * 24
                rolling = [0, -1, -2, -3, 1, 2, 3, -4, -5, 4, 5]  # roll back then forward (then back again)
                date_roll = lambda timestamp: (int(timestamp + roll_by * unix_day) for roll_by in rolling)

                for roll_date in date_roll(unix_time):
                    stock_price = getValue(stock_df, ticker.upper(), roll_date)
                    if stock_price is not None:
                        break

                for roll_date in date_roll(one_year_later):
                    stock_1y_value = getValue(stock_df, ticker.upper(), roll_date)
                    if stock_1y_value is not None:
                        break

                for roll_date in date_roll(unix_time):
                    sp500_value = getValue(sp500_df, "Adjusted Close", roll_date)
                    if sp500_value is not None:
                        break

                for roll_date in date_roll(one_year_later):
                    sp500_1y_value = getValue(sp500_df, "Adjusted Close", roll_date)
                    if sp500_1y_value is not None:
                        break

                if stock_price is None:
                    print 'No stock price for ticker %s on date %d' % (ticker, unix_time)
                    stock_price = 'N/A'
                if stock_1y_value is None:
                    print 'No stock price for ticker %s on date %d' % (ticker, one_year_later)
                    stock_1y_value = 'N/A'
                if sp500_value is None:
                    print 'No sp500 value on date %d' % unix_time
                    sp500_value = 'N/A'
                if sp500_1y_value is None:
                    print 'No sp500 value on date %d' % unix_time
                    sp500_1y_value = 'N/A'

                stock = [stock_price, stock_1y_value]
                sp500 = [sp500_value, sp500_1y_value]
                if not any(True if s=='N/A' else False for s in stock):
                    stock_p_change = round((((stock_1y_value - stock_price) / stock_price) * 100), 2)
                if not any(True if s=='N/A' else False for s in sp500):
                    sp500_p_change = round((((sp500_1y_value - sp500_value) / sp500_value) * 100), 2)

                if not any(True if s=='N/A' else False for s in stock + sp500):
                    difference = stock_p_change - sp500_p_change
                else:
                    difference = 0.

                # if difference > 5:
                #     status = "outperform"
                # else:
                #     status = "underperform"

                output_dict['difference'] = difference
                output_dict['stock_p_change'] = stock_p_change
                output_dict['sp500_p_change'] = sp500_p_change
                output_dict['stock_price'] = stock_price
                output_dict['stock_1y_value'] = stock_1y_value
                output_dict['sp500_value'] = sp500_value
                output_dict['sp500_1y_value'] = sp500_1y_value
                output_dict['ticker'] = ticker
                output_dict['Unix'] = unix_time
                output_dict['Date'] = date_stamp
                # output_dict['Status'] = status

                output_dict = dict({k: value_dict[v] for (k, v) in attributes.items()}, **output_dict)

                # nas = sum([1 for (k,v) in output_dict.items() if v == 'N/A'])

                # if nas == 0:

                output_df = output_df.append(output_dict, ignore_index=True)


    output_df.to_csv("key_stats_acc_perf_WITH_NA.csv")


Key_Stats()
