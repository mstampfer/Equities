import os
import pandas as pd

from Parser import Parser
from glob import glob

dataPath = '/Users/marcel/workspace/Equities/data/'
keyStatsPath = dataPath + 'Yahoo/intraQuarter/_KeyStats/*'
fileGlob = '[0-9]*'

p = Parser(dataPath)
tickerDirs = (e for e in glob(keyStatsPath))
filesInTickerDirs = (glob(os.path.join(d, fileGlob)) for d in tickerDirs)  # no hidden files
fullpaths = (file for files in filesInTickerDirs for file in files)
output_df = pd.DataFrame()

for fullpath in fullpaths:
    output = {}
    keyStats = {}
    ticker = p.getTickerFromFullPath(fullpath, '_KeyStats/', '/.*')
    dateStamp, unixTime = p.getDateStampAndUnixTime(os.path.basename(fullpath))

    # pull key stats from Yahoo screen
    for feature in p.features:
        value = p.searchSourceForFeature(fullpath, feature)
        value = p.cleanup(value)
        keyStats[feature] = value

    # Pull stock price and s&p adjusted close on date and forward date and clean missing values
    price = p.getValueFromDf(p.stock_df, ticker.upper(), unixTime)
    priceIn1y = p.getValueFromDf(p.stock_df, ticker.upper(), p.oneYearLater(unixTime))

    sp500 = p.getValueFromDf(p.sp500_df, 'Adjusted Close', unixTime)
    sp500In1y = p.getValueFromDf(p.sp500_df, 'Adjusted Close', p.oneYearLater(unixTime))

    # clean up
    p.setDefaultIfNone(price, unixTime)
    p.setDefaultIfNone(priceIn1y, unixTime)
    p.setDefaultIfNone(sp500, unixTime)
    p.setDefaultIfNone(sp500In1y, unixTime)

    # calculate returns and alphas
    stockReturn = p.getReturn(price, priceIn1y)
    sp500Return = p.getReturn(sp500, sp500In1y)
    if all([stockReturn, sp500Return]):
        difference = stockReturn - sp500Return
    else:
        difference = 0.0

    # concatenate key stats from screens at forward date, stock price from Quandl at forward date
    # and index value from Yahoo index at forward date
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
    output['fullpath'] = fullpath

    output = dict({k: keyStats[v] for (k, v) in p.featuresDict.items()}, **output)
    output_df = output_df.append(output, ignore_index=True)

# write output dataframe to file
output_df.to_csv("key_stats_acc_perf_WITH_NA.csv")