import os
import pandas as pd
from glob import glob


from Parser import Parser

dataPath = '/Users/marcel/workspace/Equities/data/'
keyStatsPath = dataPath + 'Yahoo/forward/data/*'
fileGlob = '*html'

p = Parser(dataPath)
fullpaths = [e for e in glob(keyStatsPath)]

output_df = pd.DataFrame()

for fullpath in fullpaths:
    output = {}
    keyStats = {}
    regex = 'market_time.....,\s(...)\s(..),\s(....)'
    ticker = p.getTickerFromFullPath(fullpath, 'forward/data/', '.html')
    forwardDate = p.getDateFromMarketTime(fullpath)
    unixTime, date = p.getDateFromMarketTime(fullpath)

    # pull key stats from Yahoo screen
    for feature in p.features:
        value = p.searchSourceForFeature(fullpath, feature)
        value = p.cleanup(value)
        keyStats[feature] = value

    # Pull stock price and s&p adjusted close on date and forward date and clean missing values
    price = p.getValueFromDf(p.stock_df, ticker.upper(), unixTime)
    priceFwd = p.getValueFromDf(p.stock_df, ticker.upper(),forwardDate)

    sp500 = p.getValueFromDf(p.sp500_df, 'Adjusted Close', unixTime)
    sp500Fwd = p.getValueFromDf(p.sp500_df, 'Adjusted Close', forwardDate)

    # clean up
    p.setDefaultIfNone(price, unixTime)
    p.setDefaultIfNone(priceFwd, unixTime)
    p.setDefaultIfNone(sp500, unixTime)
    p.setDefaultIfNone(sp500Fwd, unixTime)

    # calculate returns and alphas
    stockReturn = p.getReturn(price, priceFwd)
    sp500Return = p.getReturn(sp500, sp500Fwd)
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
    output['sp500_value'] = sp500
    output['ticker'] = ticker
    output['fullpath'] = fullpath

    output = dict({k: keyStats[v] for (k, v) in p.featuresDict.items()}, **output)
    output_df = output_df.append(output, ignore_index=True)

# write output dataframe to file
output_df.to_csv("forward_sample_ALL.csv")