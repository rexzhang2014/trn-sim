import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class StockHolding :
    '''
    Keep trading history and give functions for calculating FF(Funding Flow) and GL(Gain&Loss)
    =========================================================================================
    Imagining you have a cash account and a stock account, this class is simulation of your stock account. 
    The direction will be 1 if the funding flows from cash to stock and -1 if funding flows from stock to cash. 
    The GL is on basis of cash, if the funding flows to cash is less than that flows to stock, it is a loss and vice vesa. 
    The Holding Value is also on basis of cash, only the booking value is calculated, it equals to the value from cash to stock when you buy it.
    '''
    def __init__(self) :
        '''
        Initialization.

        Attributes
        ----------
        current : dict
            A dictionary containing symbol as keys and shares as values. It is a pointer to current holding at each date.
            Buy and Sell method will modify the content of this dict. It shows the holding at the end of the watching unit.
            *watching unit: the unit of action time. In this version, date is a watching unit,whereas the actions can only happen by end of date. 
            **Possible granularity can be defined as hour, half hour or minutes etc.This should be well defined in strategy environment, this class only treat it as a 'unit'.
            
        history : pd.DataFrame
            A DataFrame for each action item. It records actions at each watching unit. It is the source of calculaion of FF/GL.
            Schema is : ['symbol', 'date', 'shares', 'price', 'direction'], 'date' here refers to watching unit, please name your unit as 'date' no matter what in fact it is.
        '''
        self.current = {}
        self.history = pd.DataFrame(columns=['symbol', 'date', 'shares', 'price', 'direction'])
        
    def _force_date(self, s) :
        '''
        force convert input date string into python datetime datatype
        '''
        if type(s) == str :
            return datetime.strptime(s, '%Y-%m-%d')
        else :
            return s
    
    def buy(self, symbol, date, shares, price) :
        '''
        Simulate the buy action by adding one record in history dataframe, forcing history.direction = 1.

        Parameters
        ----------
        symbol : str
            A stock symbol
        date : datetime
            Buy date.
        shares : int 
            Number of shares in this transaction. No transactional constraints are maintained in this class.
        price : float
            Transaction price.
        '''
        date = self._force_date(date)
        self.history = self.history.append(
            pd.DataFrame.from_records([[symbol, date, shares, price, 1]], columns=['symbol', 'date', 'shares', 'price', 'direction']),
            ignore_index=True
        )
        if symbol in self.current.keys() :
            self.current[symbol] += shares
        else :
            self.current[symbol] = shares
            
    
    def sell(self, symbol, date, shares, price) :
        '''
        Simulate the sell action by adding one record in history dataframe, forcing history.direction = -1. 
        
        Parameters
        ----------
        symbol : str
            A stock symbol
        date : datetime
            Buy date.
        shares : int 
            Number of shares in this transaction. No transactional constraints are maintained in this class.
        price : float
            Deal price.
        '''
        date = self._force_date(date)
        self.history = self.history.append(
            pd.DataFrame.from_records([[symbol, date, shares, price, -1]], columns=['symbol', 'date', 'shares', 'price', 'direction']),
            ignore_index=True
        )
        
        if symbol in self.current.keys() :
            self.current[symbol] -= shares
            if self.current[symbol] <= 0 :
                del self.current[symbol]
        else :
            raise KeyError('{} not in current holding.'.format(symbol))
           
    def txn_cnt(self, begin, end) :
        '''
        Calculate number of transactions happened, including both buy and sell. 
        
        Parameters
        ----------
        begin : datetime
            Begin date of your watching window.
        end : datetime
            End date of your watching window.
        '''
        begin, end = self._force_date(begin), self._force_date(end)
        dt = self.history.loc[(self.history['date']>=begin) & (self.history['date']<=end) & (self.history['direction']==1), ['price', 'shares']]
        
        return dt.shape[0]
    
    def buy_amount(self, begin, end) :
        '''
        Calculate the buy amount happened in your holding history. Equivalently, the invested money between begin and end. 
        
        Parameters
        ----------
        begin : datetime
            Begin date of your watching window.
        end : datetime
            End date of your watching window.
        '''
        begin, end = self._force_date(begin), self._force_date(end)
        dt = self.history.loc[(self.history['date']>=begin) & (self.history['date']<=end) & (self.history['direction']==1), ['price', 'shares']]
        return np.sum(dt['price'] * dt['shares'])
    
    def sell_amount(self, begin, end) :
        '''
        Calculate the sell amount happened in your holding history. Equivalently, the return money between begin and end. 
        
        Parameters
        ----------
        begin : datetime
            Begin date of your watching window.
        end : datetime
            End date of your watching window.
        '''
        begin, end = self._force_date(begin), self._force_date(end)
        dt = self.history.loc[(self.history['date']>=begin) & (self.history['date']<=end) & (self.history['direction']==-1), ['price', 'shares']]
        return np.sum(dt['price'] * dt['shares'])
    
    def trading_gain(self, begin, end) :
        '''
        Calculate GL amount by selling the bought shares between begin and end. 
        
        Parameters
        ----------
        begin : datetime
            Begin date of your watching window.
        end : datetime
            End date of your watching window.
        '''
        begin, end = self._force_date(begin), self._force_date(end)
        
        buy = self.buy_amount(begin, end)
        sell = self.sell_amount(begin, end)
        
        gain = sell - buy # 交易损益 =(期间卖出 - 期间买入)
        
        return gain
    
    def holding_shares(self, begin, end) :
        '''
        Calculate how many shares are held at end date since begin date. This could be negative if begin is not from the first day in the holding history. 
        
        Parameters
        ----------
        begin : datetime
            Begin date of your watching window.
        end : datetime
            End date of your watching window.
        '''
        begin, end = self._force_date(begin), self._force_date(end)
        dt = self.history.loc[(self.history['date']>=begin) & (self.history['date']<=end), :].sort_values(['symbol', 'date'])
        dt = dt.assign(
            shr_hld = lambda x: x['shares'] * x['direction'],
        )
        
        hold = dt.groupby('symbol').agg({
            'shr_hld':np.sum, 
        })
#         print(hold)
        return hold['shr_hld']
        
    def holding_amount(self, begin, end) :
        '''
        Calculate holding amount at end date since begin date. This could be negative if begin is not from the first day in the holding history. 
        Use the last transaction price for calculation. It is the equivalent vested value if you have holding at end date.
        
        Parameters
        ----------
        begin : datetime
            Begin date of your watching window.
        end : datetime
            End date of your watching window.
        '''
        begin, end = self._force_date(begin), self._force_date(end)
        dt = self.history.loc[(self.history['date']>=begin) & (self.history['date']<=end), :].sort_values(['symbol', 'date'])
        dt = dt.assign(
            shr_hld = lambda x: x['shares'] * x['direction'],
            amt_hld = lambda x: x['shares'] * x['direction'] * x['price'],
        )
        
        hold = dt.groupby('symbol').agg({
            'shr_hld':np.sum, 
            'price': lambda x: x.tolist()[-1],
        })
#         print(hold)
        return np.sum(hold['shr_hld'] * hold['price'] )
    
    def gain(self, end) : # 建仓以来损益
        '''
        Calculate GL since first day. 
        Highly recommend to setup the end date as when the holding is cleared. 
        Otherwise the holding GL is not be included because we only calculate the vested value of your holding.
        
        On the other hand, your holding value changes along the market, only the trading gain is the real funding flow to your cach account.
        
        Parameters
        ----------
        begin : datetime
            Begin date of your watching window.
        end : datetime
            End date of your watching window.
        '''
        end = self._force_date(end)
        
        begin = self.history['date'].min()
        
# #         print(type(first_day))
#         hold_before = self.holding_amount(first_day,begin - timedelta(days=1))
        
        buy = self.buy_amount(begin, end)
        sell = self.sell_amount(begin, end)
        hold = self.holding_amount(begin, end) # 当前持仓本金
        gain = sell - buy + hold # 期间损益 = 交易损益 + 当前持仓本金 
        gain_ratio = (sell - buy + hold)/ (buy + hold) # 期间收益率 = 期间损益 / (期间买入 + 期间余额)
        
#         gain = sell - buy + hold - hold_before # 期间损益 = 交易损益 + 持仓损益 =(期间卖出 - 期间买入)+ （期末余额 - 上期末余额）
#         gain_ratio = (sell - buy + hold - hold_before)/ (buy + hold_before) # 期间收益率 = 期间损益 / (期间买入 + 期间余额)
        return gain, gain_ratio




class Strategy :
    '''
    Define your buy and sell logic. Run and see how much you can gain. 
    ==================================================================
    You need provide a watching list with at least symbol, date, price, metric. 
    Extend a child class to override the run method, where you can define your sell and buy condition and actions. 
    In general, a strategy consists of 3 elements:
        1. Environment: that is a watching list in a certain time window.
        2. Condition: a set of indicators/metrics with any value cutoff, it is usually a prediate that can be evaluated as true of false.
        3. Action: a set of actions when the condition is fulfilled. Basically it contains [buy, sell, None], more specifically, you should consider the shares and price for the actions.
    Do you find it like a Reinforcement Learning form? 
    If you want a optimal strategy, that is a way to try. 
    If you just want to verify some ideas, just define and override the self.run logic.
    '''
    def _force_date(self, s) :
        if type(s) == str :
            return datetime.strptime(s, '%Y-%m-%d')
#         elif type(s) != datetime :
#             raise ValueError('not string or date')
        else :
            return s
        
    def __init__(self, watching_list, begin, end, key='symbol', timestep='date', price='close', funding = -1, verbose=0) :
        '''
        Make up strategy instance by a market dataset and predictive score/signal. A timestep column must be specified, the column name is set as 'date' by default. 
        
        Parameters
        ----------
        watching_list : DataFrame
            Market history data set. A timestep column must be specified, the column name is set as 'date' by default. This column in the dataset will be converted as datetime type.
        begin : datetime
            Begin date of your watching window.
        end : datetime
            End date of your watching window.
        key : str
            The column name in watching_list dataset referring key of the stock.
        timestep : str
            The column name in watching_list dataset referring time step of the watching period. It can be a datetime dtype column or a date str formatted as '%Y-%m-%d' and will be converted to datetime automatically. 
        price : str
            The column name in watching_list dataset referring the price. GL calculation are based on this column's value. 
        '''
        # environment configuration
        self.watching_list = watching_list
        self.watching_list[timestep] = self.watching_list[timestep].apply(lambda x: self._force_date(x))
        
        self.begin = begin if begin else self.watching_list[timestep].min()
        self.end   = end if end else self.watching_list[timestep].max()
        
        self.available_dates = sorted(list(set(self.watching_list.loc[
            (self.watching_list[timestep]>=self.begin) & (self.watching_list[timestep]<=self.end),
            timestep
        ])))
        
        self.watching_list = self.watching_list[self.watching_list[timestep].isin(self.available_dates)]
        
        self.funding = funding # -1 means infinite funding
        self.timestep = timestep
        self.key = key
        self.price = price

        # transaction-wise configuation
        
        # Object of stock holdings
        self.holdings = StockHolding()
        self.verbose = verbose
    
    def verboseprint(self, s) :
        if self.verbose == 1 :
            print(s)
        elif self.verbose ==0 :
            pass
    
    def run(self, *args, **kwargs) :
        # override in child class
        pass 

class Criterion() :
    '''
    Strategy criterion. 
    =========================================================================================
    When the criterion is satisfied, certain actions will be taken. 
    '''
    def __init__(self) :
        '''
        Initialization.

        Attributes
        ----------
        '''
        pass    