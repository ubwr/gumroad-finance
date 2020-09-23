import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
from pandas.tseries.offsets import CustomBusinessMonthBegin
import pandas_datareader.data as web
from pandas import DataFrame
import numpy as np
import os
import backtrader as bt
import backtrader.feeds as btfeeds
import csv
import traceback 
import concurrentpandas
import time


def get_all_stocks(sp500):
    fast_panda = concurrentpandas.ConcurrentPandas()
    fast_panda.set_source_yahoo_finance()
    fast_panda.insert_keys(sp500)
    fast_panda.consume_keys_asynchronous_threads()
    mymap = fast_panda.return_map()
    return mymap


def calculate_daily(ticker, day_of_week, map):
    df = map[ticker]
    df.to_csv('Data')

    df = pd.read_csv('Data')

    df['Date'] = pd.to_datetime(df['Date'])
    df['Day of Week'] = df['Date'].dt.day_name()


    # for day_of_week in weekdays:
    temp_df = df['Day of Week'] == day_of_week
    day_of_df = df[temp_df]
    closer_higher_than_open_df = day_of_df['Close'] > day_of_df['Open']
    higher_df = day_of_df[closer_higher_than_open_df]

    day_of_df.to_csv('Data')
    day_of_df = pd.read_csv('Data',
                            header=0,
                            index_col='Date',
                            parse_dates=True)

    percent_change = 0

    for row in range(0, len(higher_df)):
        percent_change += ((higher_df.iloc[row]['Close'] /
                            higher_df.iloc[row]['Open'])-1)*100

    avg_percent_change = percent_change / len(higher_df)

    #print(ticker + ' ^ ' + day_of_week + ' | ' + str(round(((len(higher_df)/len(day_of_df))*100), 2))+'%'+' |'
    #      + ' AVG CHG | ' + str(round((avg_percent_change), 2)) + '% |')
    return_hashmap = {'Probability': float(round(
        ((len(higher_df)/len(day_of_df))*100), 2)), 'Average_Change': float(round((avg_percent_change), 2))}
    return return_hashmap


def insert_data_labels(bars, ax):
    for bar in bars:
        bar_height = bar.get_height()
        ax.annotate(str('{:.2f}'.format(bar.get_height()) + '%'),
                    xy=(bar.get_x() + bar.get_width() / 2, bar_height),
                    xytext=(0, 3),
                    textcoords='offset points',
                    ha='center',
                    va='bottom')


def calculate_monthly(ticker, start, end):

    df = web.get_data_yahoo(ticker, start, end)

    ohlc_dict = {'Open': 'first', 'High': 'max', 'Low': 'min',
                 'Close': 'last', 'Volume': 'sum', 'Adj Close': 'last'}
    mthly_ohlcva = df.resample('M').agg(ohlc_dict)

    temp_var = 0

    mthly_ohlcva.to_csv('Data')

    mthly_ohlcva = pd.read_csv('Data')

    percent_change = 0

    for row in range(0, len(mthly_ohlcva)):
        if (mthly_ohlcva.iloc[row]['Close']) > (mthly_ohlcva.iloc[row-1]['Close']):
            percent_change += ((mthly_ohlcva.iloc[row]['Close'] /
                                mthly_ohlcva.iloc[row-1]['Close'])-1)*100

    avg_percent_change = percent_change / len(mthly_ohlcva)

    for row in range(0, len(mthly_ohlcva)):
        if (mthly_ohlcva.iloc[row]['Close']) < (mthly_ohlcva.iloc[row-1]['Close']):
            temp_var += 1
            #print(str(temp_var) + ' ' + str(mthly_ohlcva.iloc[row]['Date']))
        if row == len(mthly_ohlcva) - 1:
            print(ticker + ' ! Monthly | ' + str(round((temp_var / len(mthly_ohlcva)*100), 2))+'%'
                  + ' |' + ' AVG CHG | ' + str(round((avg_percent_change), 2)) + '% |')


def calculate_weekly(ticker, start, end):
    df = web.DataReader(ticker, 'yahoo', start, end)

    ohlc_dict = {'Open': 'first', 'High': 'max',
                 'Low': 'min', 'Close': 'last', }

    wkly_ohlcva = df.resample('W').agg(ohlc_dict)

    percent_change = 0
    temp_var = 0
    for row in range(0, len(wkly_ohlcva)):
        if (wkly_ohlcva.iloc[row]['Close']) > (wkly_ohlcva.iloc[row-1]['Close']):
            temp_var += 1
            # print(temp_var)
            percent_change += ((wkly_ohlcva.iloc[row]['Close'] /
                                wkly_ohlcva.iloc[row-1]['Close'])-1)*100

    avg_percent_change = percent_change / len(wkly_ohlcva)
    # print(len(wkly_ohlcva))

    temp_var = 0

    for row in range(0, len(wkly_ohlcva)):
        # if not (wkly_ohlcva.iloc[row]['Close']) > (wkly_ohlcva.iloc[row-1]['Close']) and not (wkly_ohlcva.iloc[row]['Close']) < (wkly_ohlcva.iloc[row-1]['Close']):
        if (wkly_ohlcva.iloc[row]['Close']) > (wkly_ohlcva.iloc[row-1]['Close']):
            temp_var += 1

        if row == len(wkly_ohlcva) - 1:
            print(ticker + ' ^ Weekly | ' + str(round((temp_var / len(wkly_ohlcva)*100), 2))+'%'
                  + ' |' + ' AVG CHG | ' + str(round((avg_percent_change), 2)) + '% |')


def save_plot(plot, ticker):
    filename = ticker + ".png"
    plot.savefig(filename)


def load_tickers():
    list = []
    with open('sp500.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='"')
        for row in spamreader:
            #fix lookups in yahoo finance
            list.append(row[0])
            print(', '.join(row))
    return list


def plot_daily(daily_df, start, end, stock_ticker):
        indx = np.arange(len(daily_df['Percent']))
        percent_label = np.arange(0, 110, 10)
        bar_width = 0.35
        fig, ax = plt.subplots()
        percent_bar = ax.bar(indx - bar_width/2,
                            daily_df['Percent'], bar_width, label='Percent')
        avg_change_bar = ax.bar(
            indx + bar_width/2, daily_df['Average Change'], bar_width, label='Average Change')
        ax.set_xticks(indx)
        ax.set_xticklabels(daily_df['Day of the Week'])
        ax.set_yticks(percent_label)
        ax.set_yticklabels(percent_label)
        ax.set_ylabel('Percentage')
        ax.set_xlabel('Day of the week')
        ax.legend()
        ax.set_title(stock_ticker + ' % historic closing up on a given weekday from ' + str(start.year) + '-' + str(start.month) + '-' + str(start.day)
                    + ' to ' + str(end.year) + '-' + str(end.month) + '-' + str(end.day))

        insert_data_labels(percent_bar, ax)
        insert_data_labels(avg_change_bar, ax)
        fig.set_size_inches(12, 9)

        plt.savefig("./stock_charts/" + stock_ticker)


def calc_historic(stock_ticker, stock_map):
    style.use('ggplot')

    monday = calculate_daily(stock_ticker, 'Monday', stock_map)
    tuesday = calculate_daily(stock_ticker, 'Tuesday', stock_map)
    wednesday = calculate_daily(stock_ticker, 'Wednesday', stock_map)
    thursday = calculate_daily(stock_ticker, 'Thursday', stock_map)
    friday = calculate_daily(stock_ticker, 'Friday', stock_map)

    daily_df = DataFrame({
        'Day of the Week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
        'Percent': [
            monday['Probability'],
            tuesday['Probability'],
            wednesday['Probability'],
            thursday['Probability'],
            friday['Probability']
        ],
        'Average Change':
        [
            monday['Average_Change'],
            tuesday['Average_Change'],
            wednesday['Average_Change'],
            thursday['Average_Change'],
            friday['Average_Change']
        ]})

    return daily_df


def get_remaining_stocks(start, end, tickers, trys_remaining):
    print("Attempts remaining: " + str(trys_remaining))
    
    if len(tickers) < 1:
        return 0

    if trys_remaining <= 0:
        return 0
    if trys_remaining <= 7 and trys_remaining > 3:
        time.sleep(900)
    if trys_remaining <= 3 and trys_remaining > 1:
        time.sleep(1800)
    if trys_remaining == 1:
        time.sleep(2700)

    all_stocks = get_all_stocks(tickers)
    retry_list = []
    for ticker in tickers:
        if ticker in all_stocks:
            try:
                data = calc_historic(ticker, all_stocks)
                plot_daily(data, start, end, ticker)
            except:
                retry_list.append(ticker)
                print(str(ticker) + " failed to plot")
        else:
            retry_list.append(ticker)

    for stock in retry_list:
        print(stock + " failed to download, or failed to plot and will recursively retry now.")
    
    get_remaining_stocks(start, end, retry_list, trys_remaining-1)


def main():
    start = dt.datetime(2019, 8, 2)
    end = dt.datetime(2020, dt.datetime.now().month, dt.datetime.now().day)

    tickers = load_tickers()
    get_remaining_stocks(start, end, tickers, 10)

    

startTime = time.time()
main()

executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))
