import os
from datetime import datetime
from glob import glob
from time import mktime
import pandas as pd

import re


class Parser:
    def __init__(self, dataPath):

        self.featuresDict = {'DE Ratio': 'Total Debt/Equity',
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
        self.features = self.featuresDict.values()

        self.path = dataPath
        self.statspath = self.path + 'Yahoo/intraQuarter/_KeyStats'
        self.tickerDirs = (x[0] for x in os.walk(self.statspath))
        self.filesInTickerDirs = (glob(os.path.join(d, '[0-9]*')) for d in self.tickerDirs)  # no hidden files
        self.files = (file for files in self.filesInTickerDirs for file in files)
        self.tickers = (dir.split("_KeyStats/")[1] for dir in self.tickerDirs)
        self.unix_day = 60 * 60 * 24
        self.rolling = [0, -1, -2, -3, 1, 2, 3, -4, -5, 4, 5]  # roll back then forward (then back again)
        self.date_roll = lambda timestamp: (int(timestamp + roll_by * self.unix_day) for roll_by in self.rolling)

        self.sp500_df = pd.DataFrame.from_csv(self.path + "Yahoo/YAHOO-INDEX_GSPC.csv")
        self.stock_df = pd.DataFrame.from_csv(self.path + "Quandl/stock_prices.csv")




    def getDateStampAndUnixTime(self, filename):
        dateStamp = datetime.strptime(filename, '%Y%m%d%H%M%S.html')
        unixTime = mktime(dateStamp.timetuple())
        return dateStamp, unixTime

    def getTickerFromFile(self, file):
        regex = '_KeyStats/' + '(.*)' + '/.*'
        value = re.search(regex, file)
        ticker = value.group(1)
        return ticker

    def searchSourceForFeature(self, file, feature):
        source = open(file, 'r').read()
        try:
            regex = '(' + feature + ')' + r'.*?\n?\s*?.*?tabledata1">\n?\r?\s*?(-?(\d{1,3},)?\d{1,8}(\.\d{1,8})?M?B?K?|N/A)\%?\n?\r?\s*?</td>'
            value = re.search(regex, source)
            value = (value.group(2))
        except Exception:

            try:
                regex = '(' + feature + ')' + r'.*?\n?\t*?\s*?.*?\n?.*?tabledata1">\n?\r?\s*?(-?(\d{1,3},)?\d{1,8}(\.\d{1,8})?M?B?|N/A)\%?\n?\r?\s*?</td>'
                value = re.search(regex, source)
                value = (value.group(2))
            except:
                print 'Warning cannot find %s for ticker %s in file %s. ' % (feature, self.getTickerFromFile(file), file)
                value = "N/A"
        return value

    def getValue(self, df, attribute, timestamp):
        try:
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            row = df[(df.index == date)]
            value = float(row[attribute])
            return value
        except:
            return None

    def getValueFromDf(self, df, string, unix_time):
        value = None
        for roll_date in self.date_roll(unix_time):
            value = self.getValue(df, string, roll_date)
            if value is not None:
                break
        return value

    def setDefaultIfNone(self, value, unix_time):
        if value is None:
            print 'No sp500 value on date %d' % unix_time
            value = 'N/A'

    def cleanup(self, value):
        if ',' in str(value):
            value = value.replace(',', '')

        if "B" in value:
            value = float(value.replace("B", '')) * 1000000000.

        elif "M" in value:
            value = float(value.replace("M", '')) * 1000000.

        elif "K" in value:
            value = float(value.replace("K", '')) * 1000.

        return value

    def oneYearLater(self, unix_time):
        return int(unix_time + 31536000)

    def getReturn(self, old, new):
        l = [old, new]
        if all(False if s=='N/A' else True for s in l):
            return round((((new - old) / old) * 100), 2)
        else:
            return None

p = Parser('/Users/marcel/workspace/Equities/data/')
output = {}
values = {}
for file in p.files:
    ticker = p.getTickerFromFile(file)
    for feature in p.features:
        value = p.searchSourceForFeature(file, feature)
        value = p.cleanup(value)
        values[feature] = value

    dateStamp, unixTime = p.getDateStampAndUnixTime(file)
    price = p.getValueFromDf(p.stock_df, ticker.upper(), unixTime)
    priceIn1y = p.getValueFromDf(p.stock_df, ticker.upper(), p.oneYearLater(unixTime))
    sp500 = p.getValueFromDf(p.sp500_df, 'Adj_Close', unixTime)
    sp500In1y = p.getValueFromDf(p.sp500_df, 'Adj_Close', p.oneYearLater(unixTime))
    p.setDefaultIfNone(price, unixTime)
    p.setDefaultIfNone(priceIn1y, unixTime)
    p.setDefaultIfNone(sp500, unixTime)
    p.setDefaultIfNone(sp500In1y, unixTime)
    stockReturn = p.getReturn(price, priceIn1y)
    sp500Return = p.getReturn(sp500, sp500In1y)
    if all([stockReturn, sp500Return]):
        difference = stockReturn - sp500Return
    else:
        difference = 0.0


    output['difference'] = difference
    output['stock_p_change'] = stockReturn
    output['sp500_p_change'] = sp500Return
    output['stock_price'] = price
    output['stock_1y_value'] = priceIn1y
    output['sp500_value'] = sp500
    output['sp500_1y_value'] = sp500In1y
    output['ticker'] = ticker
    output['Unix'] = unixTime
    output['Date'] = dateStamp

    output = dict({k: values[v] for (k, v) in p.featuresDict.items()}, **output)









