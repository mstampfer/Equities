import pandas as pd
import os
from datetime import datetime

from time import mktime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style
style.use("dark_background")

from glob import glob

import re


path = '/Users/marcel/workspace/data/'


def getValue(df, attribute, timestamp):
    try:
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        row = df[(df.index == date)]
        value = float(row[attribute])
        return value
    except:
        return None


def Key_Stats(gather=["Total Debt/Equity",
                      'Trailing P/E',
                      'Price/Sales',
                      'Price/Book',
                      'Profit Margin',
                      'Operating Margin',
                      'Return on Assets',
                      'Return on Equity',
                      'Revenue Per Share',
                      'Market Cap',
                        'Enterprise Value',
                        'Forward P/E',
                        'PEG Ratio',
                        'Enterprise Value/Revenue',
                        'Enterprise Value/EBITDA',
                        'Revenue',
                        'Gross Profit',
                        'EBITDA',
                        'Net Income Avl to Common ',
                        'Diluted EPS',
                        'Earnings Growth',
                        'Revenue Growth',
                        'Total Cash',
                        'Total Cash Per Share',
                        'Total Debt',
                        'Current Ratio',
                        'Book Value Per Share',
                        'Cash Flow',
                        'Beta',
                        'Held by Insiders',
                        'Held by Institutions',
                        'Shares Short (as of',
                        'Short Ratio',
                        'Short % of Float',
                        'Shares Short (prior ']):
    
    statspath = path+'intraQuarter/_KeyStats'
    stock_list = [x[0] for x in os.walk(statspath)]
    sp500_df = pd.DataFrame.from_csv(path+"YAHOO-INDEX_GSPC.csv")
    stock_df = pd.DataFrame.from_csv(path+"output/stock_prices.csv")

    ticker_list = []
    output_df = pd.DataFrame()

    for each_dir in stock_list[1:]:
        files = glob(os.path.join(each_dir, '[0-9]*'))  # no hidden files
        ticker = each_dir.split("_KeyStats/")[1]
        ticker_list.append(ticker)

##        starting_stock_value = False
##        starting_sp500_value = False

        
        if len(files) > 0:
            for full_file_path in files:
                file = os.path.basename(full_file_path)
                date_stamp = datetime.strptime(file, '%Y%m%d%H%M%S.html')
                unix_time = mktime(date_stamp.timetuple())
                source = open(full_file_path,'r').read()
                try:
                    value_list = []

                    for each_data in gather:
                        try:
                            regex = re.escape(each_data) + r'.*?(\d{1,8}\.\d{1,8}M?B?|N/A)%?'
                            value = re.search(regex, source)
                            value = (value.group(1))

                        if value == None:
                            pass
                        if "B" in value:
                            value = float(value.replace("B",''))*1000000000.

                        elif "M" in value:
                            value = float(value.replace("M",''))*1000000.

                        elif "K" in value:
                            value = float(value.replace("K",''))*1000.

                        value_dict[each_data] = value

                            
                        except Exception as e:
                            value = "N/A"
                            value_list.append(value)

                    one_year_later = int(unix_time + 31536000)
                    stock_price, sp500_value, stock_1y_value, sp500_1y_value = None, None, None, None

                    unix_day = 60*60*24
                    rolling = [0, -1, -2, -3, 1, 2, 3, -4, -5, 4, 5]  # roll back then forward (then back again)
                    date_roll = lambda timestamp: (int(timestamp+roll_by*unix_day) for roll_by in rolling)

                    for time in date_roll(unix_time):
                        stock_price = getValue(stock_df, ticker.upper(), time)
                        if stock_price is not None:
                            break
                    if stock_price is None:
                        print 'No stock price for ticker %s on date %d' %(ticker, unix_time)

                    for time in date_roll(one_year_later):
                        stock_1y_value = getValue(stock_df, ticker.upper(), time)
                        if stock_1y_value is not None:
                            break
                    if stock_1y_value is None:
                        print 'No stock price for ticker %s on date %d' %(ticker, one_year_later)

                    for time in date_roll(unix_time):
                        sp500_value = getValue(sp500_df, "Adjusted Close", time)
                        if sp500_value is not None:
                            break
                    if sp500_value is None:
                        print 'No sp500 value on date %d' % unix_time

                    for time in date_roll(one_year_later):
                        sp500_1y_value = getValue(sp500_df, "Adjusted Close", time)
                        if sp500_1y_value is not None:
                            break
                    if sp500_1y_value is None:
                        print 'No sp500 value on date %d' % unix_time



                    stock_p_change = round((((stock_1y_value - stock_price) / stock_price) * 100), 2)
                    sp500_p_change = round((((sp500_1y_value - sp500_value) / sp500_value) * 100), 2)

                    
                    difference = stock_p_change-sp500_p_change

                    if difference > 0:
                        status = "outperform"
                    else:
                        status = "underperform"


                    # if value_list.count("N/A") > 0:
                    #     pass
                    # else:
                        
                output_df = output_df.append({'Date':date_stamp,
                                 'Unix':unix_time,
                                 'Ticker':ticker,
                                 'Price':stock_price,
                                 'stock_p_change':stock_p_change,
                                 'SP500':sp500_value,
                                 'sp500_p_change':sp500_p_change,
                                 'Difference':difference,
                                 'DE Ratio':value_dict['Total Debt/Equity'].replace(",",""),
                                 'Trailing P/E':value_dict['Trailing P/E'].replace(",",""),
                                 'Price/Sales':value_dict['Price/Sales'].replace(",",""),
                                 'Price/Book':value_dict['Price/Book'].replace(",",""),
                                 'Profit Margin':value_dict['Profit Margin'].replace(",",""),
                                 'Operating Margin':value_dict['Operating Margin'].replace(",",""),
                                 'Return on Assets':value_dict['Return on Assets'].replace(",",""),
                                 'Return on Equity':value_dict['Return on Equity'].replace(",",""),
                                 'Revenue Per Share':value_dict['Revenue Per Share'].replace(",",""),
                                 'Market Cap':value_dict['Market Cap'],
                                 'Forward P/E':value_dict['Forward P/E'].replace(",",""),
                                 'PEG Ratio':value_dict['PEG Ratio'].replace(",",""),
                                 'Enterprise Value':value_dict['Enterprise Value'],
                                 # 'Enterprise Value/Revenue':value_dict['Enterprise Value/Revenue'].replace(",",""),
                                 # 'Enterprise Value/EBITDA':value_dict['Enterprise Value/EBITDA'].replace(",",""),
                                 'Revenue':value_dict['Revenue'],
                                 'Gross Profit':value_dict['Gross Profit'],
                                 'EBITDA':value_dict['EBITDA'],
                                 'Net Income Avl to Common ':value_dict['Net Income Avl to Common '],
                                 'Earnings Per Share':value_dict['Earnings Per Share|Diluted EPS'].replace(",",""),
                                 'Earnings Growth':value_dict['Earnings Growth'].replace(",",""),
                                 'Revenue Growth':value_dict['Revenue Growth'].replace(",",""),
                                 'Total Cash':value_dict['Total Cash'],
                                 'Total Cash Per Share':value_dict['Total Cash Per Share'].replace(",",""),
                                 'Total Debt':value_dict['Total Debt'],
                                 'Current Ratio':value_dict['Current Ratio'].replace(",",""),
                                 'Book Value Per Share':value_dict['Book Value Per Share'].replace(",",""),
                                 'Operating Cash Flow': value_dict['From Operations|Operating Cash Flow'],
                                 'Beta':value_dict['Beta'].replace(",",""),
                                 'Held by Insiders':value_dict['Held by Insiders'].replace(",",""),
                                 'Held by Institutions':value_dict['Held by Institutions'].replace(",",""),
                                 'Shares Short':value_dict['Shares Short'],
                                 'Short Ratio':value_dict['Short Ratio'],
                                 'Short % of Float':value_dict['Short % of Float'],
                                 'Status':status},
                               ignore_index=True)

                except Exception as e:
                    print str(e)


    output_df.to_csv("key_stats_acc_perf_NO_NA.csv")
    

Key_Stats()