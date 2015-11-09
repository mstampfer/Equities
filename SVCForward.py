from matplotlib import use
use('TkAgg')
import numpy as np
from sklearn import preprocessing
# from sklearn.feature_selection.univariate_selection import GenericUnivariateSelect
import pandas as pd
from matplotlib import style
style.use('ggplot')
from Selection import Selection
import PlotLearningCurve
from GridSearchParams import GridSearchParams, RandomParamSearch
from sklearn import cross_validation


from sklearn import svm

# how_much_better = 5

def status_calc(stock_p_change, sp500_p_change):

    difference = stock_p_change-sp500_p_change
    if difference > 10:
        return 1
    else:
        return 0


path = '/Users/marcel/workspace/Equities/data/'
FEATURES =  [#'stock_price',
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
             'Forward P/E',
             'PEG Ratio',
             'Enterprise Value',
             'Revenue',
             'Gross Profit',
             'EBITDA',
             'Net Income Avl to Common ',
             'Earnings Per Share',
             'Earnings Growth',
             'Revenue Growth',
             'Total Cash',
             'Total Cash Per Share',
             'Total Debt',
             'Current Ratio',
             'Book Value Per Share',
             'Operating Cash Flow',
             'Beta',
             'Held by Insiders',
             'Held by Institutions',
             'Shares Short',
             'Short Ratio',
             'Short % of Float']

def Build_Data_Set(file, features):
    data_df = pd.DataFrame.from_csv(file, parse_dates=['Date'])

    data_df = data_df.reindex(np.random.permutation(data_df.index))
    data_df = data_df.replace('N/A',0).replace('NaN',0)
    data_df['Status'] = map(status_calc, data_df['stock_p_change'], data_df['sp500_p_change'])


    X = np.array(data_df[features].values)
    X = preprocessing.scale(X)
    y = data_df['Status']

    # # test/train 60/40 spliy
    # X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.4, random_state=0)


    return X, y


def Analysis():

    cv_size = 1000
    file = path + 'key_stats_acc_perf_NO_NA.csv'

    X, y = Build_Data_Set(file, FEATURES)

    clf = svm.SVC(kernel='rbf', C=1)

    # scores = cross_validation.cross_val_score(clf, X, y, cv=3, n_jobs=2, verbose=True) # hangs
    scores = cross_validation.cross_val_score(clf, X, y, cv=5, verbose=True, scoring='precision') # 0.71

    print("Precision: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

    # Best C selection
    # sel = Selection(X, y, FEATURES, cv_size)
    # bestC = sel.selectC(X, y)

    # PlotLearningCurve.learningCurve(X,y)

    # GridSearchParams(X, y)

    RandomParamSearch(X, y)
    # for x in range(cv_size + 1):
    #     if clf.predict(X[-x])[0] == 1:
    #         invest_return = invest_amount + invest_amount * alpha[-x][0] / 100.
    #         market_return = invest_amount + invest_amount * alpha[-x][1] / 100.
    #         total_invests += 1
    #         if_market += market_return
    #         if_strat += invest_return


    #
    # data_df = pd.DataFrame.from_csv(path+'forward_sample_WITH_NA.csv')
    # data_df = data_df.replace('N/A',0).replace('NaN',0)
    #
    # invest_list = []
    #
    # X = np.array(data_df[FEATURES].values)
    # X = preprocessing.scale(X)
    # tickers = data_df['ticker'].values.tolist()
    #
    # for i in range(len(X)):
    #     p = clf.predict(X[i])[0]
    #     if p == 1:
    #         print tickers[i]
    #         invest_list.append(tickers[i])
    #
    # print len(invest_list)
    # print invest_list
    #
    # ts_dict = {name: pd.Series(group['stock_price'].values, index=group['Date'].values) for (name, group) in Z.groupby('ticker')}
    #
    # for e in invest_list:
    #     if e in ts_dict.keys():
    #         ts_dict[e].plot()
    #         plt.xlabel('date')
    #         plt.ylabel('stock price')
    # plt.show()

Analysis()