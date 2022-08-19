#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install oandapy


# In[2]:


import configparser 
import oandapy as opy  

config = configparser.ConfigParser()  
config.read('oanda.cfg')  

oanda = opy.API(environment='practice',
                access_token=config['oanda']['access_token'])  


# In[4]:


import pandas as pd  

data = oanda.get_history(instrument='EUR_USD',
                         start='2016-12-08',  
                         end='2016-12-10',  
                         granularity='M1')  

df = pd.DataFrame(data['candles']).set_index('time')  

df.index = pd.DatetimeIndex(df.index)  


df.info()


# In[5]:


import numpy as np  

df['returns'] = np.log(df['closeAsk'] / df['closeAsk'].shift(1))  

cols = []  

for momentum in [15, 30, 60, 120]:
    col = 'position_%s' % momentum  
    df[col] = np.sign(df['returns'].rolling(momentum).mean())  
    cols.append(col)  


# In[6]:


get_ipython().run_line_magic('matplotlib', 'inline')
import seaborn as sns; sns.set()  

strats = ['returns'] 

for col in cols:  
    strat = 'strategy_%s' % col.split('_')[1]  
    df[strat] = df[col].shift(1) * df['returns'] 
    strats.append(strat)  

df[strats].dropna().cumsum().apply(np.exp).plot()


# In[7]:


class MomentumTrader(opy.Streamer):  
    def __init__(self, momentum, *args, **kwargs):  
        opy.Streamer.__init__(self, *args, **kwargs)  
        self.ticks = 0  
        self.position = 0  
        self.df = pd.DataFrame()  
        self.momentum = momentum  
        self.units = 100000  
    def create_order(self, side, units):  
        order = oanda.create_order(config['oanda']['account_id'], 
            instrument='EUR_USD', units=units, side=side,
            type='market')  
        print('\n', order)  
    def on_success(self, data):  
        self.ticks += 1  
        self.df = self.df.append(pd.DataFrame(data['tick'],
                                 index=[data['tick']['time']])) 
        self.df.index = pd.DatetimeIndex(self.df['time']) 
        dfr = self.df.resample('5s').last()  
        dfr['returns'] = np.log(dfr['ask'] / dfr['ask'].shift(1)) 
        dfr['position'] = np.sign(dfr['returns'].rolling( 
                                      self.momentum).mean())  
        if dfr['position'].ix[-1] == 1:  
            if self.position == 0:  
                self.create_order('buy', self.units)  
            elif self.position == -1:  
                self.create_order('buy', self.units * 2) 
            self.position = 1 
        elif dfr['position'].ix[-1] == -1: 
            if self.position == 0: 
                self.create_order('sell', self.units)  
            elif self.position == 1: 
                self.create_order('sell', self.units * 2)  
            self.position = -1  
        if self.ticks == 250:  
            if self.position == 1:  
                self.create_order('sell', self.units)  
            elif self.position == -1: 
                self.create_order('buy', self.units)  
            self.disconnect() 


# In[8]:


mt = MomentumTrader(momentum=12, environment='practice',
                    access_token=config['oanda']['access_token'])
mt.rates(account_id=config['oanda']['account_id'],
         instruments=['DE30_EUR'], ignore_heartbeat=True)


# In[ ]:




