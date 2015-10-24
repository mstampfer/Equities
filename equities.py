import pandas as pd
import os
import time
from datetime import datetime
from time import mktime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import style

style.use('dark_background')
import re
from glob import glob

path = '/Users/marcel/workspace/data/intraQuarter'


def Key_Stats(gather={"Total Debt/Equity",
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
                      'Earnings Per Share',
                      'Earnings Growth',
                      'Revenue Growth',
                      'Total Cash',
                      'Total Cash Per Share',
                      'Total Debt',
                      'Current Ratio',
                      'Book Value Per Share',
                      'From Operations',
                      'Operating Cash Flow',
                      'Beta',
                      'Held by Insiders',
                      'Held by Institutions',
                      'Shares Short',  # .as of|Shares Short .prior|Shares Short',
                      'Short Ratio',
                      'Short % of Float'}):
    statspath = path + '/_KeyStats'
    stock_list = [x[0] for x in os.walk(statspath)]
    df = pd.DataFrame(columns = ['Date',
                                 'Unix',
                                 'Ticker',
                                 'Price',
                                 'stock_p_change',
                                 'SP500',
                                 'sp500_p_change',
                                 'Difference',
                                 'DE Ratio',
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
                                 'From Operations',
                                 'Operating Cash Flow',
                                 'Beta',
                                 'Held by Insiders',
                                 'Held by Institutions',
                                 'Shares Short',
                                 'Short Ratio',
                                 'Short % of Float',
                                 'Status'])

    sp500_df = pd.DataFrame.from_csv("YAHOO-INDEX_GSPC.csv")

    ticker_list = []

    for each_dir in stock_list[1:]:
        each_file = glob(os.path.join(each_dir, '[0-9]*'))  # no hidden files
        ticker = each_dir.split("_KeyStats/")[1]

        starting_stock = False
        starting_sp500 = False

        if len(each_file) > 0:
            for file in each_file:
                try:
                    date_stamp = datetime.strptime(os.path.basename(file), '%Y%m%d%H%M%S.html')
                except:
                    pass
                unix_time = time.mktime(date_stamp.timetuple())
                source = open(file, 'r').read()

                value_dict = {}
                # # DE Ratio
                # try:
                #     de_ratio = source.split(gather + ':</td><td class="yfnc_tabledata1">')[1].split('</td>')[0]
                # except:
                #     try:
                #         de_ratio = source.split(gather + ':</td>\n<td class="yfnc_tabledata1">')[1].split('</td>')[
                #             0]
                #     except:
                #         try:
                #             de_ratio = \
                #             source.split(gather + ':</td>\r\n<td class="yfnc_tabledata1">')[1].split('</td>')[0]
                #         except:
                #             pass

                for each_data in gather:
                    try:
                        regex = each_data + r'.*?\n?\s*?.*?tabledata1">\n?\r?\s*?(-?\d{1,8}(\.\d{1,8})?M?B?K?|N/A)\%?\n?\r?\s*?</td>'
                        value = re.search(regex, source)
                        value = (value.group(1))

                        if "B" in value:
                            value = float(value.replace("B",''))*1000000000

                        elif "M" in value:
                            value = float(value.replace("M",''))*1000000

                        value_dict[each_data] = value


                    except Exception:
                        try:
                            regex = each_data + r'.*?\n?\t*?\s*?.*?\n?.*?tabledata1">\n?\r?\s*?(-?\d{1,8}(\.\d{1,8})?M?B?|N/A)\%?\n?\r?\s*?</td>'
                            value = re.search(regex, source)
                            value = (value.group(1))
                            value_dict[each_data] = value
                        except:
                            if "Operat" not in each_data and "Earnings Per Share" not in each_data :
                                print 'Warning cannot find %s for ticker %s. ' % (each_data, ticker)
                            value = "N/A"
                            value_dict[each_data] = value

                # pull S&P value on tick date
                try:
                    sp500_date = datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d')
                    row = sp500_df[(sp500_df.index == sp500_date)]
                    sp500_value = float(row["Adjusted Close"])
                except:
                    try:
                        sp500_date = datetime.utcfromtimestamp(unix_time - 259200).strftime('%Y-%m-%d')
                        row = sp500_df[(sp500_df.index == sp500_date)]
                        sp500_value = row["Adjusted Close"]
                        sp500_value = float(sp500_value)
                    except:
                        print "Warning no S&P data found for date %s" % sp500_date
                        continue
                # stock price
                try:
                    s = source.split('</small><big><b>')[1].split('</b></big>')[0]
                    stock_price = float(s)
                except:

                    try:
                        s = source.split('<span id="yfs_l10_' + ticker + '">')[1].split('</span>')[0]
                        stock_price = float(s)
                    except:

                        try:
                            s = source.split('<span id="yfs_l84_' + ticker + '">')[1].split('</span>')[0]
                            stock_price = float(s)
                        except:
                            try:
                                s = re.search('(\d{1,8}\.\d{1,8})', s)
                                stock_price = float(s.group(1))
                            except Exception as e:
                                print 'Warning cannot find stock price for following:'
                                print str(e), stock_price, ticker, file
                                pass


                # print("stock_price:", stock_price, "ticker:", ticker)

                if not starting_stock:
                    starting_stock_value = stock_price
                    starting_stock = True
                if not starting_sp500:
                    starting_sp500_value = sp500_value
                    starting_sp500 = True

                stock_p_change = (stock_price - starting_stock_value) / starting_stock_value * 100.0
                sp500_p_change = (sp500_value - starting_sp500_value) / starting_sp500_value * 100.0

                difference = stock_p_change - sp500_p_change
                try:
                    if difference > 0.0:
                        status = 'outperform'
                    else:
                        status = 'underperform'
                except:
                    print 'Warning cannot set status for ticker %s' % ticker
                    pass

                na_count = sum(1 for val in value_dict.values() if val == 'N/A')
                if na_count > 0:
                    pass


                df = df.append({'Date':date_stamp,
                                 'Unix':unix_time,
                                 'Ticker':ticker,
                                 'Price':stock_price,
                                 'stock_p_change':stock_p_change,
                                 'SP500':sp500_value,
                                 'sp500_p_change':sp500_p_change,
                                 'Difference':difference,
                                 'DE Ratio':value_dict['Total Debt/Equity'],
                                 #'Market Cap':value_dict[1],
                                 'Trailing P/E':value_dict['Trailing P/E'],
                                 'Price/Sales':value_dict['Price/Sales'],
                                 'Price/Book':value_dict['Price/Book'],
                                 'Profit Margin':value_dict['Profit Margin'],
                                 'Operating Margin':value_dict['Operating Margin'],
                                 'Return on Assets':value_dict['Return on Assets'],
                                 'Return on Equity':value_dict['Return on Equity'],
                                 'Revenue Per Share':value_dict['Revenue Per Share'],
                                 'Market Cap':value_dict['Market Cap'],
                                 'Enterprise Value':value_dict['Enterprise Value'],
                                 'Forward P/E':value_dict['Forward P/E'],
                                 'PEG Ratio':value_dict['PEG Ratio'],
                                 'Enterprise Value/Revenue':value_dict['Enterprise Value/Revenue'],
                                 'Enterprise Value/EBITDA':value_dict['Enterprise Value/EBITDA'],
                                 'Revenue':value_dict['Revenue'],
                                 'Gross Profit':value_dict['Gross Profit'],
                                 'EBITDA':value_dict['EBITDA'],
                                 'Net Income Avl to Common ':value_dict['Net Income Avl to Common '],
                                 'Diluted EPS':value_dict['Diluted EPS'],
                                 'Earnings Growth':value_dict['Earnings Growth'],
                                 'Revenue Growth':value_dict['Revenue Growth'],
                                 'Total Cash':value_dict['Total Cash'],
                                 'Total Cash Per Share':value_dict['Total Cash Per Share'],
                                 'Total Debt':value_dict['Total Debt'],
                                 'Current Ratio':value_dict['Current Ratio'],
                                 'Book Value Per Share':value_dict['Book Value Per Share'],
                                 'From Operations':value_dict['From Operations'],
                                 'Operating Cash Flow': value_dict['Operating Cash Flow'],
                                 'Beta':value_dict['Beta'],
                                 'Held by Insiders':value_dict['Held by Insiders'],
                                 'Held by Institutions':value_dict['Held by Institutions'],
                                 'Shares Short':value_dict['Shares Short'],
                                 'Short Ratio':value_dict['Short Ratio'],
                                 'Short % of Float':value_dict['Short % of Float'],
                                 'Status':status},
                               ignore_index=True)
                ticker_list.append(ticker)

    # for each_ticker in ticker_list:
    #
    #     try:
    #         plot_df = df[(df['Ticker'] == each_ticker)]
    #         if plot_df['Status'].values[-1] == 'underperform':
    #             color = 'r'
    #         else:
    #             color = 'g'
    #
    #         plot_df = plot_df.set_index(['Date'])
    #         plot_df['Difference'].plot(label=each_ticker, color=color)
    #     except Exception as e:
    #         print e
    #         print 'Warning cannot set label for ticker %s' % each_ticker
    #         pass
    # plt.legend()
    # plt.show(block=False)

    df.to_csv("key_stats.csv")
    raw_input('Enter to close')


Key_Stats()
