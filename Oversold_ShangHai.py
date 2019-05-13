# -*- encoding: utf8 -*-
#这个暂时不用，感觉没啥用，还超时。


import tushare as ts
from datetime import *
import numpy as np
from matplotlib.pyplot import plot
from matplotlib.pyplot import show
#import firsttrade as ft

def sma(sp):
    N=15
    n=np.ones(N)
    weights=n/N
    sma=np.convolve(weights,sp)[N-1:-N+1]
    return sma

#Exponential Moving Average
def ema(sp):
    N=15
    weights=np.exp(np.linspace(0,1,N))
    weights =weights/np.sum(weights)
    ema=np.convolve(weights,sp)[N-1:-N+1]
    return ema

def rsi_buy(stock_code):
    dt =datetime.now() ;
    start_date =(dt -timedelta(days=50)).strftime('%Y-%m-%d')

    end_date =(dt ).strftime('%Y-%m-%d')
    all_price = ts.get_k_data(stock_code,start=start_date,end=end_date)
    u_array =np.zeros_like(all_price['close'], dtype=np.float  )#np.array(dtype=np.float)
    d_array =np.zeros_like(all_price['close'], dtype=np.float  )
    count = 0
    for i in all_price.index:
      if count == 0 :
        count = count+ 1
        continue
      day_close = all_price.get_value(i,'close')
      day_open = all_price.get_value(i-1,'close')

      if day_close > day_open:
          u_array[count] = day_close - day_open
          d_array[count] = 0
      elif   day_close < day_open:
          d_array[count] = day_open - day_close
          u_array[count] = 0
      else:
          u_array[count] = 0
          d_array[count] = 0
      count = count+ 1          
    ema_u = ema(u_array)
    ema_d = ema(d_array)
    rsi = ema_u /(ema_u + ema_d)
    if rsi.__getitem__(rsi.size-1) < 0.2:
       return True
    print( stock_code +' ,RSI:' +str( rsi.__getitem__(rsi.size-1)) )
    return False
    


def va_buy(stock_code):
    dt =datetime.now() ;
    start_date =(dt -timedelta(days=500)).strftime('%Y-%m-%d')

    end_date =(dt -timedelta(days=150)).strftime('%Y-%m-%d')
    all_price = ts.get_k_data(stock_code,start=start_date,end=end_date)
    max_date = all_price[all_price['close']== max(all_price['close'])]['date']
    total_share = 0
    total_pay = 0
    curr_buy = 0
    curr_period = 0
    amount_per_period = 1000
    
    for every_day in all_price['date']:
        #every_ticker = [all_price['date']== max_date]
        if every_day> max_date.get_values().all():
            every_ticker = all_price[all_price['date']== every_day]
            curr_period = curr_period + 1
            aim_amount = curr_period * amount_per_period 
            curr_amount =total_share * float(every_ticker['close'])
            curr_buy =int( (aim_amount - curr_amount ) /float(every_ticker['close']))
            total_pay = total_pay + curr_buy * float(every_ticker['close'])
            total_share = total_share + curr_buy
    if total_share *float(all_price.tail(1)['close']) /total_pay >1.9:
        print("buy:"+stock_code)
        return True;
    return False;

def gen_va_buy_list():
  buy_list =[];
  all_stocks=ts.get_stock_basics()
  if  all_stocks is None:
    print('取基本信息错误')
    exit();
  for stock in all_stocks.index:
    stockdata= all_stocks.loc[stock]
    try:
      if float(stockdata['totalAssets']) >1000  \
         and float(stockdata['esp']) >0 \
         and float(stockdata['gpr']) >5  \
         and  float(stockdata['pe']) < 50  :
         
        print('basic suggestion:'+stock )
        if va_buy(stock):
           buy_list.append(stock)
           #ft.auto_buy(stock, 100)
    except:
        print ("Error:"+ stock)
    
  print(buy_list)

def gen_rsi_buy_list():
  buy_list =[];
  all_stocks=ts.get_stock_basics()
  if  all_stocks is None:
    print('取基本信息错误')
    exit();
  for stock in all_stocks.index:
    stockdata= all_stocks.loc[stock]
    try:
      if float(stockdata['totalAssets']) >1000  \
         and float(stockdata['esp']) >0 \
         and float(stockdata['gpr']) >5  \
         and  float(stockdata['pe']) < 50  :
         
        #print('basic suggestion:'+stock )
        if rsi_buy(stock):
           buy_list.append(stock)
           #ft.auto_buy(stock, 100)
    except:
        print ("Error:"+ stock)
    
  print(buy_list)

  
if __name__ == '__main__':
  gen_va_buy_list()