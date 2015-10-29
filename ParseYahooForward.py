import os
import re
import pandas as pd


path = '/Users/marcel/workspace/data/'
attributes = {'DE Ratio'                        :'Total Debt/Equity',
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

def Forward():

    gather = attributes.values()
    file_list = os.listdir(path + "output/forward")
    output_df = pd.DataFrame()

    for each_file in file_list:

        ticker = each_file.split(".html")[0]
        full_file_path = path + "output/forward/" + each_file
        source = open(full_file_path, "r").read()
        print ticker
        value_dict = {}
        output_dict = {}
        for each_data in gather:
            try:
                regex = '(' + each_data + ')' + r'.*?\n?\s*?.*?tabledata1">\n?\r?\s*?(-?(\d{1,3},)?\d{1,8}(\.\d{1,8})?M?B?K?|N/A)\%?\n?\r?\s*?</td>'
                value = re.search(regex, source)
                value = (value.group(2))

                if ',' in str(value):
                    value = value.replace(',', '')

                if "B" in value:
                    value = float(value.replace("B", '')) * 1000000000.

                elif "M" in value:
                    value = float(value.replace("M", '')) * 1000000.

                elif "K" in value:
                    value = float(value.replace("K", '')) * 1000.

                value_dict[each_data] = value

            except Exception:
                try:
                    regex = '(' + each_data + ')' + r'.*?\n?\t*?\s*?.*?\n?.*?tabledata1">\n?\r?\s*?(-?(\d{1,3},)?\d{1,8}(\.\d{1,8})?M?B?|N/A)\%?\n?\r?\s*?</td>'
                    value = re.search(regex, source)
                    value = (value.group(2))
                    value_dict[each_data] = value

                except Exception as e:
                    print 'Warning cannot find %s for ticker %s in file %s. ' % (each_data, ticker, each_file)
                    value = "N/A"
                    value_dict[each_data] = value

        output_dict['ticker'] = ticker
        output_dict = dict({k: value_dict[v] for (k, v) in attributes.items()}, **output_dict)
        nas = sum([1 for (k,v) in output_dict.items() if v == 'N/A'])

        if nas == 0:
            output_df = output_df.append(output_dict, ignore_index=True)

    output_df.to_csv("forward_sample_WITH_NA.csv")

Forward()