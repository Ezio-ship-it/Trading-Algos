# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 05:01:01 2024

@author: Ezio
"""

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mplfinance as mpf

length = 10
mult = 2.0
calc_method = 'Atr'

def calculate_atr(data, length):
    high = data['High']
    low = data['Low']
    close = data['Close']
    tr1 = high - low  #curr high-low
    tr2 = abs(high - close.shift(1)) #curr day high - prevday close
    tr3 = abs(low - close.shift(1))#curr day low - prev day close
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(window=length).mean() #atr val


def calculate_pivots(data, length):
    pivot_high = data['High'].rolling(window=2*length+1, center=True).apply(lambda x: x.iloc[length] == max(x)) #window inc (left,center,right),x[iloc] for peak high
    pivot_low = data['Low'].rolling(window=2*length+1, center=True).apply(lambda x: x.iloc[length] == min(x)) #peak low
    return pivot_high, pivot_low


symbol = "RECLTD.NS"
start_date = "2024-05-01"#yyyy-mm-dd
end_date = "2024-07-05"
tf="60m"

data = yf.download(symbol, start=start_date, end=end_date,interval=tf)


pivot_high, pivot_low = calculate_pivots(data, length)


if calc_method == 'Atr':
    slope = calculate_atr(data, length) / length * mult #ascending & descending slop , multiplier based adjustment


upper = pd.Series(index=data.index, dtype=float) #var to store all data points
lower = pd.Series(index=data.index, dtype=float)


for i in range(len(data)):
    if pivot_high.iloc[i]:
        upper.iloc[i] = data['High'].iloc[i]
    elif i > 0:
        upper.iloc[i] = upper.iloc[i-1] - slope.iloc[i] #Down slope if curr high is not highest
    
    if pivot_low.iloc[i]:
        lower.iloc[i] = data['Low'].iloc[i]
    elif i > 0:
        lower.iloc[i] = lower.iloc[i-1] + slope.iloc[i] #Up slope is curr low is not lowest


upward_breakout = (data['Close'] > upper) & (data['Close'].shift(1) <= upper.shift(1)) #Close above upper chanel & check if prev day close is under chanel or not
downward_breakout = (data['Close'] < lower) & (data['Close'].shift(1) >= lower.shift(1)) #Close below lower chanel 
 

upward_markers = pd.Series(np.where(upward_breakout, data['Low'], np.nan), index=data.index) # Breakout and breakdown arrow
downward_markers = pd.Series(np.where(downward_breakout, data['High'], np.nan), index=data.index)


additional_plots = [
    mpf.make_addplot(upper, color='green', width=1),
    mpf.make_addplot(lower, color='red', width=1),
    mpf.make_addplot(upward_markers, type='scatter', markersize=100, marker='^', color='green'),
    mpf.make_addplot(downward_markers, type='scatter', markersize=100, marker='v', color='red'),
]

mpf.plot(data, type='candle', style='charles',
         title=f"{symbol} - Trendline breakout",
         addplot=additional_plots,
         figsize=(15, 7))

#print(upper.tail())
#print(lower.tail())
#print(upward_breakout[upward_breakout == True])
#print(downward_breakout[downward_breakout == True])