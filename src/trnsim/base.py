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
    def __init__(self, *args, **kwargs) :
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
    
    def txn_cost(self, begin, end, unit_cost=1) :
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
        
        return dt.shape[0] * unit_cost

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
        gain_ratio = (sell - buy + hold)/ (buy + hold + 0.0001) # 期间收益率 = 期间损益 / (期间买入 + 期间余额)
        
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
        
    def __init__(self, watching_list, begin, end, key='symbol', timestep='date', price='close', funding = -1, max_portion=0.5, verbose=0) :
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
        
        self.initial_funding = funding # keep intial funding value. -1 means infinite funding
        self.funding = funding # change the funding if action is taken. 
        self.timestep = timestep
        self.key = key
        self.price = price

        # transaction-wise configuation
        self.max_portion = max_portion

        # Object of stock holdings
        self.holdings = StockHolding()
        self.verbose = verbose

        # Performance attributes
        self.net_values = []
        self.stats = []

    def verboseprint(self, s) :
        if self.verbose == 1 :
            print(s)
        elif self.verbose ==0 :
            pass
    
    def _select_snapshot(self, *args, **kwargs) :
        dt= args[0]
        selected = self.watching_list[self.watching_list[self.timestep] == dt] 
        return selected

    def _select_champion(self, snapshot, *args, **kwargs) :
        return snapshot.head(10)
        
    def _sell_all(self, snapshot, dt, *args, **kwargs) :
        tosell = set(self.holdings.current.keys())        
        dates = self.available_dates
        p_dt  = dates[dates.index(dt) + 1]

        for s in tosell :
            try :
                p = snapshot.loc[
                    (snapshot[self.key]==s) & (snapshot[self.timestep]==p_dt), 
                    self.price
                ].tolist()[0]
                sh = self.holdings.current[s]
                self.verboseprint('{} sell {} shares of stock {} at price {}'.format(str(p_dt)[:10], sh, s, p))
                self.holdings.sell(s, p_dt, sh, p)
            except Exception as e:
                print(repr(e))

        # update current funding
        self.funding += self.holdings.sell_amount(p_dt, p_dt)

    def _sell(self, snapshot, champion, dt, *args, **kwargs) :
        # Define the stocks in holding but not in champion is possible to be sold.
        tosell = set(self.holdings.current.keys()) - set(champion[self.key])
        dates = self.available_dates
        p_dt  = dates[dates.index(dt) + 1]

        for s in tosell :
            try :
                p = snapshot.loc[
                    (snapshot[self.key]==s) & (snapshot[self.timestep]==p_dt), 
                    self.price
                ].tolist()[0]

                # get current shares
                sh = self.holdings.current[s]
                self.verboseprint('{} sell {} shares of stock {} at price {}'.format(str(p_dt)[:10], sh, s, p))
                # take sell action and update holding history
                self.holdings.sell(s, p_dt, sh, p)

            except Exception as e:
                print(repr(e))

        # update current funding
        self.funding += self.holdings.sell_amount(p_dt, p_dt)

    def _buy(self, snapshot, champion, dt, *args, **kwargs) :
        # Define the stocks in champion is possible to be bought.
        tobuy = set(champion[self.key]) - set(self.holdings.current.keys())
        dates = self.available_dates
        p_dt  = dates[dates.index(dt) + 1]
        
        portion = kwargs.get('portion', len(tobuy))
        portion = 1 / portion * self.max_portion if portion > 1 else self.max_portion
        for s in tobuy :
            try :
                p = snapshot.loc[
                    (snapshot[self.key]==s) & (snapshot[self.timestep]==p_dt), 
                    self.price
                ].tolist()[0]

                # calculate how many shares to buy
                sh = portion * self.funding // (p*100) * 100
                if sh > 0 :
                    # take buy action and update holding history
                    self.verboseprint('{} buy {} shares of stock {} at price {}'.format(str(p_dt)[:10], sh, s, p))
                    self.holdings.buy(s, p_dt, sh, p)
                else :
                    self.verboseprint('Warning: Insufficient Fund:{}'.format(self.funding))
    
            except Exception as e:
                print(repr(e))

        # update current funding
        buy_amt = self.holdings.buy_amount(p_dt, p_dt) 
        self.funding -= buy_amt


    def _calc_perf(self) :
        output = {
            'initial_funding': self.initial_funding,
            'current_funding': self.funding,
            'current_net_value': self.stats[-1]['net_value'],
            'net_value_gain': self.stats[-1]['net_value'] -1,
            'buy_amount' : self.holdings.buy_amount(self.begin, self.end), 
            'sell_amount' : self.holdings.sell_amount(self.begin, self.end), 
            'hold_amount' : self.holdings.holding_amount(self.begin, self.end), 
            'current_holding' : self.holdings.current, 
            'trading_gain' : self.holdings.trading_gain(self.begin, self.end), 
            'gain' : self.holdings.gain(self.end), 
            'txn_cnt' : self.holdings.txn_cnt(self.begin, self.end),   
        }
        return output

    def _available_dates(self) :
        return self.available_dates

    def net_value(self, dt, *args, **kwargs) :
        fund = self.funding
        holding_value = 0
        snaps = self.watching_list[self.watching_list[self.timestep]==dt]

        for stk, shr in self.holdings.current.items() :
            p = snaps.loc[snaps[self.key]==stk, self.price].values[0]
            holding_value  += p * shr
        return round((fund + holding_value) / self.initial_funding, 6)

    def run(self, *args, **kwargs) :

        # For each dt(assuming the timestep is in date manner), we evaluate :
        # 1. whether the current holding is to be sold 
        # 2. whether there are stocks not in the holding to be bought
        # 0. Clear the position if dt is the last date in simulation time window, to simplify performance calculation. 
        for dt in self._available_dates() :

            # Pick the snapshot fulfilling conditions for next calculation, the simplest one is to take current_dt as the only input.
            snapshot = self._select_snapshot(dt)
            # Select the candidate stocks pool from the ranking_metrics/indicators in the simulated data.
            champion = self._select_champion(snapshot)
            
            # 0. at last day, assume we clear the holdings
            if dt == self.available_dates[-1] : 
                self._sell_all(snapshot, dt)
                break
                
            # 1. sell holdings that are out of topk
            self._sell(snapshot, champion, dt)

            # 2. buy topk on that day with today's close price (assume we are able to do this in next day, before next closing.)
            self._buy(snapshot, champion, dt)

            self.verboseprint(self.holdings.current)
                    
            self.verboseprint('trading gain: {} , gain: {}'.format(self.holdings.trading_gain(self.begin, dt), self.holdings.gain(dt)))
            
            # self.net_values.append({
            #     'date' : dt,
            #     'net_value' : self.net_value(dt),
            # })

            self.stats.append({
                'date' : dt, 
                'net_value' : self.net_value(dt),
                'txn_cnt': self.holdings.txn_cnt(dt, dt),
                'current_funding' : self.funding,
            })
            # self.verboseprint('current funding:{}, net_value:{}'.format(self.funding, self.net_values[-1]['net_value']))
            print('{}: current funding:{}, net_value:{}'.format(dt, self.funding, self.stats[-1]['net_value']))

        output = self._calc_perf()
        
        return output

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