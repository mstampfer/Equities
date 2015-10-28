import os
import urllib2
import time

path = '/Users/marcel/workspace/data/'

def Check_Yahoo():
    statspath = path + 'intraQuarter/_KeyStats/'
    stock_list = [x[0] for x in os.walk(statspath)]

    try:
        for e in stock_list[1:]:
            e = e.replace(statspath, '')
            if e > 'znga':
                link = 'http://finance.yahoo.com/q/ks?s=%s+Key+Statistics' % e.upper()
                response = urllib2.urlopen(link)
                html = response.read()
                print(e)

                save = '%soutput/forward/%s.html' % (path, str(e))
                store = open(save, 'w')
                store.write(str(html))
                store.close()
                time.sleep(1)

    except Exception as e:
        print str(e)

Check_Yahoo()

raw_input('Enter to exit')


