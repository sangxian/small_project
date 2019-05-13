# -*- encoding: utf8 -*-

#三因子选股模型，市场超额收益，规模（outstanding）和账面市值比（市净率的倒数，1/pb）

#后续计划使用的因子：流通股本 outstanding、固定资产比例 fixedAssets/totalAssets、市盈 pe、账面市值比(市净率的倒数，1/pb)、
#净利润 （net_profits），每股现金流量（epcf） 等 因子选股，每月第一天轮换一次。
import tushare as ts
import time
import numpy as np
import pandas as pd
#加载画图需要用的包
import matplotlib as mpl
import matplotlib.pyplot as plt

import seaborn as sns

#mpl.style.use('ggplot')

from dask.dataframe.core import DataFrame


def   get_profit_report():
  year = time.strftime("%Y",time.localtime())
  month = time.strftime("%m",time.localtime())
  season= int(int(month)/3)
  
  df =ts.get_profit_data(int(year),season)
  
  if df is None:
    season = season - 1;
    df =ts.get_profit_data(int(year),season)
  else: 
    if str(df.head(1).roe[0])=='nan':
       season = season - 1
       df =ts.get_profit_data(int(year),season)

  
  return df;

'''
获取股票的 因子信息，根据 规模(S,B)，账面市值比率(H,M,L ) 分成6组。
'''
def get_6groups():   #
    basicdata=ts.get_stock_basics()
    #profitdata=get_profit_report()
    #breakpoint=filter(lambda x:x.isdigit(),C.iat[len(C)-1,1])                         #取breakpoint前最近一个交易日日期
    zz500=ts.get_zz500s()
    if  zz500 is None:
      print('获取中证500 成份股失败')
      exit();
    ME=basicdata.loc[zz500['code'],['name','outstanding','pb']]
    ME['pb']=1/ME['pb']
    ME50=np.percentile(ME['outstanding'],50)   
    S=ME[ME['outstanding']<=ME50].index.tolist()   #按市值大小分为两组，存为列表
    B=ME[ME['outstanding']>ME50].index.tolist()
    BP30=np.percentile(ME['pb'],30)
    BP70=np.percentile(ME['pb'],70)
    L=ME[ME['pb']<=BP30].index.tolist()  #按1/PB大小分为三组
    H=ME[ME['pb']>BP70].index.tolist()
    M=list(set(ME.index.tolist()).difference(set(L+H)))
    SL=list(set(S).intersection(set(L)))      #对S组和L组的股票取交集，作为SL组的股票组合
    SM=list(set(S).intersection(set(M)))
    SH=list(set(S).intersection(set(H)))
    BL=list(set(B).intersection(set(L)))
    BM=list(set(B).intersection(set(M)))
    BH=list(set(B).intersection(set(H)))
    return SL,SM,SH,BL,BM,BH 
    
    
    '''
    ME=set(basicdata['name','outstanding']).intersection(set(zz500['name']))..dropna()   #取当时的市值
    ME50=np.percentile(ME['outstanding'],50)                                     #算出市值大小的50%分位值
    S=ME[ME['outstanding']<=ME50]['ticker'].tolist()                                #按市值大小分为两组，存为列表
    B=ME[ME['outstanding']>ME50]['ticker'].tolist()
    BP=DataAPI.MktStockFactorsOneDayGet(tradeDate=breakpoint,secID=universe,field=u"ticker,pb").dropna() 
    BP=BP[BP>0].dropna()                                                  #去掉PB值为负的股票
    BP[['pb']]=1/BP[['pb']]                                                #取1/pb，为账面市值比
    '''
    
   
'''
下面我们要计算每个投资组合的 季度 (Season)收益率，
计算投资组合的季收益率时，要算市值加权的收益率，这是为了最小化方差（风险）

'''
def get_returnSeason(x,Year):
    # 
    basicdata=ts.get_stock_basics()
    basicdata=basicdata.loc[x,['name','outstanding']]
    basicdata['code']=basicdata.index
    #profitdata=get_profit_report['code','name','roe']
    returnSeasonly=np.zeros(4)
    
    for i in range(4):
      pd = ts.get_profit_data(Year,i+1)
      while pd is None:
        pd = ts.get_profit_data(Year,i+1)
        
      pd = pd.loc[:,['code','roe']]
      pd =pd.dropna()
      
      #pd.index =pd[pd.code<>np.nan]
      pd.index =pd['code']
      Return =pd.loc[x,['code','roe']]
      if len(Return)==0 :
          print('空数据，不处理 '+str(Year)+str(i))
          returnSeasonly[i]=0
          break
      Return['weight'] =basicdata['outstanding']/ basicdata['outstanding'].sum()
      Return['Wreturn'] = Return['weight']*Return['roe']
      returnSeasonly[i] = Return['Wreturn'].sum()
      if i>0 :
          returnSeasonly[i]=returnSeasonly[i]-returnSeasonly[i-1]
      print('已处理 '+str(Year)+str(i))
    return returnSeasonly



if __name__ == '__main__':
  #basicdata=ts.get_stock_basics();
  #profitdata=get_profit_report();
  SL,SM,SH,BL,BM,BH =get_6groups()
  #r_SL =get_returnSeason(SL,'');
  #计算每年的SMB和HML因子，合在一起,
  SMB=[]
  HML=[]
  r_groups=pd.DataFrame()  #用于存储每个组合的月收益率序列，方便我们之后查看
  r_510500=pd.DataFrame()
  r_groups['SL']=np.zeros(36)
  r_groups['SM']=np.zeros(36)
  r_groups['SH']=np.zeros(36)
  r_groups['BL']=np.zeros(36)
  r_groups['BM']=np.zeros(36)
  r_groups['BH']=np.zeros(36)
  r_510500['zz500']=np.zeros(36)
  zz500=ts.get_zz500s()
  for Year in [2007,2008,2009,2010,2011,2012,2013,2014,2015]:
    #获取  中证500 当年的季度收益率. 
    r_510500_S=get_returnSeason(list(zz500['code']),Year)
    r_510500.iloc[(Year-2007)*4:(Year-2006)*4,[0]]=r_510500_S.reshape(4,1)

    r_SL=get_returnSeason(SL,Year)       #得到当年5月末到次年的市值加权月收益率序列
    r_SM=get_returnSeason(SM,Year)
    r_SH=get_returnSeason(SH,Year)
    r_BL=get_returnSeason(BL,Year)
    r_BM=get_returnSeason(BM,Year)
    r_BH=get_returnSeason(BH,Year)
    
    r_groups.iloc[(Year-2007)*4:(Year-2006)*4,[0]]=r_SL.reshape(4,1)   #把组合SL当年5月末到次年的市值加权月收益率序列
    r_groups.iloc[(Year-2007)*4:(Year-2006)*4,[1]]=r_SM.reshape(4,1)
    r_groups.iloc[(Year-2007)*4:(Year-2006)*4,[2]]=r_SH.reshape(4,1)
    r_groups.iloc[(Year-2007)*4:(Year-2006)*4,[3]]=r_BL.reshape(4,1)
    r_groups.iloc[(Year-2007)*4:(Year-2006)*4,[4]]=r_BM.reshape(4,1)
    r_groups.iloc[(Year-2007)*4:(Year-2006)*4,[5]]=r_BH.reshape(4,1)
    SMBr=(r_SL+r_SM+r_SH)/3-(r_BL+r_BM+r_BH)/3                         #当年的SMB和HML因子，存为list
    HMLr=(r_SH+r_BH)/2-(r_SL+r_BL)/2   
    SMB += SMBr.tolist()
    HML += HMLr.tolist()
  SMB=np.array(SMB)
  HML=np.array(HML)
  r_groups.plot(figsize=[12,7])
  
  #计算市场利率时，使用510500的收益率
  
  RmMonthly = r_510500
  RfMonthly=np.zeros(36)+1.5
  
  MF=RmMonthly['zz500']-RfMonthly
  factor=pd.DataFrame()
  factor['MF']=MF
  factor['SMB']=SMB
  factor['HML']=HML
  #factor.index=date[1:]
  factor.plot(figsize=[12,7])
  factor.describe()
  
  
  x=np.zeros((3,36))
  x[0]=MF
  x[1]=SMB
  x[2]=HML
  Correlations=pd.DataFrame(np.corrcoef(x))
  Correlations.columns=['MF','SMB','HML']
  Correlations.index=['MF','SMB','HML']
  Correlations
  a=1;
  
  
  
  