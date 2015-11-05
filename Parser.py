from datetime import datetime
from time import mktime
import pandas as pd
import time
import re


class Parser(object):
    def __init__(self, path):

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
        self.path = path
        self.features = self.featuresDict.values()
        self.unix_day = 60 * 60 * 24
        self.rolling = [0, -1, -2, -3, 1, 2, 3, -4, -5, 4, 5]  # roll back then forward (then back again)
        self.date_roll = lambda timestamp: (int(timestamp + roll_by * self.unix_day) for roll_by in self.rolling)
        self.sp500_df = pd.DataFrame.from_csv(self.path + "Yahoo/YAHOO-INDEX_GSPC.csv")
        self.stock_df = pd.DataFrame.from_csv(self.path + "Quandl/stock_prices.csv")

    def getDateStampAndUnixTime(self, filename):
        dateStamp = datetime.strptime(filename, '%Y%m%d%H%M%S.html')
        unixTime = mktime(dateStamp.timetuple())
        return dateStamp, unixTime

    def getTickerFromFullPath(self, fullpath, preceed, proceed):
        regex = preceed + '(.*)' + proceed
        value = re.search(regex, fullpath)
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
                print 'Warning cannot find %s for ticker %s in file %s. ' % (feature, self.getTickerFromFullPath(file), file)
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
            print 'No sp500 value on %s' % datetime.fromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
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
        if all(False if s=='N/A' or s==None else True for s in l):
            return round((((new - old) / old) * 100), 2)
        else:
            return None

    def getDateFromMarketTime(self, fullpath):
        regex = 'market_time.....,\s(...)\s(..),\s(....)'
        source = open(fullpath, "r").read()
        value = re.search(regex, source)
        month = (value.group(1))
        day = (value.group(2))
        year = (value.group(3))
        date = datetime.strptime('%s-%s-%s' %(day,month,year), '%d-%b-%Y')
        unix_time = int(time.mktime(date.timetuple()))
        return unix_time, date








