import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
from pandas.tseries.offsets import CustomBusinessMonthBegin
import pandas_datareader.data as web
from pandas import DataFrame
import numpy as np


today = dt.datetime.today()
style.use('ggplot')
start = dt.datetime(2019, 8, 7)

tick = 'AAPL'

#end = dt.datetime(today.year, today.month, today.day)
end = dt.datetime(2020, 8, 7)
#end = dt.datetime(today.year, today.month, today.day)
#end = dt.datetime(start.year+1, start.month, start.day)

#print('Start date: ' + str(start))
#print('End date: ' + str(end))


def calculate_daily(ticker, day_of_week):
    df = web.DataReader(ticker, 'yahoo', start, end)
    df.to_csv('Data')
    
    df = pd.read_csv('Data')

    df['Date'] = pd.to_datetime(df['Date'])
    df['Day of Week'] = df['Date'].dt.day_name()

    #daily_df = DataFrame({'% chance of closing up in daily time frame':[]})

    #for day_of_week in weekdays:
    temp_df = df['Day of Week']==day_of_week
    day_of_df = df[temp_df]
    closer_higher_than_open_df = day_of_df['Close'] > day_of_df['Open']
    higher_df = day_of_df[closer_higher_than_open_df]

    percent_change = 0

    for row in range(0, len(higher_df)):
        percent_change += ((higher_df.iloc[row]['Close'] / higher_df.iloc[row]['Open'])-1)*100

    avg_percent_change = percent_change / len(higher_df)

##    print(ticker + ' ^ ' + day_of_week + ' | ' + str(round(((len(higher_df)/len(day_of_df))*100), 2))+'%'+' |'
##          + ' AVG CHG | ' + str(round((avg_percent_change), 2)) + '% |')

    return [round(((len(higher_df)/len(day_of_df))*100), 2), round((avg_percent_change), 2)]

##for year in range(0, (dt.datetime.today().year)-start.year):
##    calculate_daily()
##    print('__________________________')
##    start.year += 1

#calculate_daily()

daily_df = DataFrame({'Day of the Week':['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                      'Percent': [calculate_daily(tick, 'Monday')[0], calculate_daily(tick, 'Tuesday')[0], calculate_daily(tick, 'Wednesday')[0], calculate_daily(tick, 'Thursday')[0], calculate_daily(tick, 'Friday')[0]],
                      'Average Change': [calculate_daily(tick, 'Monday')[1], calculate_daily(tick, 'Tuesday')[1], calculate_daily(tick, 'Wednesday')[1], calculate_daily(tick, 'Thursday')[1], calculate_daily(tick, 'Friday')[1]]})

##ax = daily_df.plot.bar(x='Day of the Week', y='Percent', rot=0)
##
##ax.set_title('Chance of closing up per weekday from ' + str(start.year) + '-' + str(start.month) + '-' + str(start.day)
##             + ' to ' + str(end.year) + '-' + str(end.month) + '-' + str(end.day))
##
##plt.show()

########################################################################

indx = np.arange(len(daily_df['Percent']))
percent_label = np.arange(0, 110, 10)
bar_width = 0.35
fig, ax = plt.subplots()
percent_bar = ax.bar(indx - bar_width/2, daily_df['Percent'], bar_width, label='Percent')
avg_change_bar = ax.bar(indx + bar_width/2, daily_df['Average Change'], bar_width, label='Average Change')
ax.set_xticks(indx)
ax.set_xticklabels(daily_df['Day of the Week'])
ax.set_yticks(percent_label)
ax.set_yticklabels(percent_label)
ylab = ax.set_ylabel('Percentage')
xlab = ax.set_xlabel('Day of the week')
ax.legend()
ax.set_title(tick + ' % chance of closing up per weekday from ' + str(start.year) + '-' + str(start.month) + '-' + str(start.day)
             + ' to ' + str(end.year) + '-' + str(end.month) + '-' + str(end.day))

##print(0%2)
##print(1%2)
##print(2%2)
##print(3%2)

def insert_data_labels(bars):
##    temp = 0
    for bar in bars:
            bar_height = bar.get_height()
##            if temp % 2 == 0:
##                bar.set_color('g')
##            else:
##                bar.set_color('b')
##            temp += 1
            ax.annotate(str('{:.2f}'.format(bar.get_height()) + '%'),
                xy=(bar.get_x() + bar.get_width() / 2, bar_height),
                xytext=(0, 3),
                textcoords='offset points',
                ha='center',
                va='bottom')

insert_data_labels(percent_bar)
insert_data_labels(avg_change_bar)

plt.show()

########################################################################

print(daily_df)




def calculate_monthly(ticker):
    

    df = web.get_data_yahoo(ticker, start, end)
        
    ohlc_dict = {'Open':'first','High':'max','Low':'min','Close': 'last','Volume': 'sum','Adj Close': 'last'}
    mthly_ohlcva = df.resample('M').agg(ohlc_dict)

    temp_var = 0

    mthly_ohlcva.to_csv('Data')

    mthly_ohlcva = pd.read_csv('Data')
    
    percent_change = 0

    for row in range(0, len(mthly_ohlcva)):
        if (mthly_ohlcva.iloc[row]['Close']) > (mthly_ohlcva.iloc[row-1]['Close']):
            percent_change += ((mthly_ohlcva.iloc[row]['Close'] / mthly_ohlcva.iloc[row-1]['Close'])-1)*100


    avg_percent_change = percent_change / len(mthly_ohlcva)
    
    for row in range(0, len(mthly_ohlcva)):            
            if (mthly_ohlcva.iloc[row]['Close']) < (mthly_ohlcva.iloc[row-1]['Close']):
                temp_var += 1
                #print(str(temp_var) + ' ' + str(mthly_ohlcva.iloc[row]['Date']))
            if row == len(mthly_ohlcva) - 1:
                print(ticker + ' ! Monthly | ' + str(round((temp_var / len(mthly_ohlcva)*100), 2))+'%'
                      + ' |' + ' AVG CHG | ' + str(round((avg_percent_change), 2)) + '% |')
                

#calculate_monthly(tick)




def calculate_weekly(ticker):
    df = web.DataReader(ticker, 'yahoo', start, end)

    ohlc_dict = {'Open':'first','High':'max','Low':'min','Close': 'last',}
    
    wkly_ohlcva = df.resample('W').agg(ohlc_dict)

    percent_change = 0
    temp_var = 0
    for row in range(0, len(wkly_ohlcva)):
        if (wkly_ohlcva.iloc[row]['Close']) > (wkly_ohlcva.iloc[row-1]['Close']):
            temp_var += 1
            #print(temp_var)
            percent_change += ((wkly_ohlcva.iloc[row]['Close'] / wkly_ohlcva.iloc[row-1]['Close'])-1)*100
            


    avg_percent_change = percent_change / len(wkly_ohlcva)
    #print(len(wkly_ohlcva))

    temp_var = 0
    

    for row in range(0, len(wkly_ohlcva)):
        #if not (wkly_ohlcva.iloc[row]['Close']) > (wkly_ohlcva.iloc[row-1]['Close']) and not (wkly_ohlcva.iloc[row]['Close']) < (wkly_ohlcva.iloc[row-1]['Close']):
        if (wkly_ohlcva.iloc[row]['Close']) > (wkly_ohlcva.iloc[row-1]['Close']):    
            temp_var += 1
##            print(wkly_ohlcva.iloc[row])
##            print(str(temp_var))
##            print(wkly_ohlcva.iloc[row-1])
        if row == len(wkly_ohlcva) - 1:
            print(ticker + ' ^ Weekly | ' + str(round((temp_var / len(wkly_ohlcva)*100), 2))+'%'
                    + ' |' + ' AVG CHG | ' + str(round((avg_percent_change), 2)) + '% |')
                      

#calculate_weekly(tick)

##SNP 500, 100
##GOLD
##OIL
##DIVDEND KING STOCKS
#rsi open and rsi close, rsi 14 period and rsi 21 period
#not only checking if it went up %, but also by what % did it avg going up on those days
#horizontal bar graph for daily ?
#same green day date as red day date?