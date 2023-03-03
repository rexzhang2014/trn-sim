
from .base import *

class BuyEqualAmountTopKAndHoldTDay(Strategy) :
    def __init__(self, ranking_metric, topk=10, spare_amount=200000, hold_days=5, *args, **kwargs) :
        Strategy.__init__(self, *args, **kwargs)
        # selection-wise configuration
        self.ranking_metric = ranking_metric
        self.topk = topk
        self.spare_amount = spare_amount 
        self.hold_days = hold_days
    
    def _available_dates(self) :
        return self.available_dates[::self.hold_days]  + self.available_dates[-1:]
    
    def _select_snapshot(self, *args, **kwargs) :
        dt= args[0]
        selected = self.watching_list[self.watching_list[self.timestep] == dt] 
        return selected

    def _select_champion(self, snapshot) :
        selected = snapshot.sort_values(self.ranking_metric, ascending=False).head(self.topk)
        return selected

    def _sell(self, snapshot, champion, dt, *args, **kwargs) :
        # Define the stocks in holding but not in champion is possible to be sold.
        tosell = set(self.holdings.current.keys()) - set(champion[self.key])
        for s in tosell :
            try :
                p = snapshot.loc[snapshot[self.key]==s, self.price].tolist()[0]
                sh = self.holdings.current[s]
                self.verboseprint('{} sell {} shares of stock {} at price {}'.format(str(dt)[:10], sh, s, p))
                self.holdings.sell(s, dt, sh, p)
            except Exception as e:
                print(repr(e))

    def _buy(self, snapshot, champion, dt, *args, **kwargs) :
        # Define the stocks in champion is possible to be bought.
        tobuy = set(champion[self.key]) - set(self.holdings.current.keys())
        for s in tobuy :
            try :
                p = snapshot.loc[snapshot[self.key]==s, self.price].tolist()[0]
                sh = self.spare_amount // (p*100)
                
                self.verboseprint('{} buy {} shares of stock {} at price {}'.format(str(dt)[:10], sh, s, p))
                
                self.holdings.buy(s, dt, sh, p)
            except Exception as e:
                print(repr(e))

class BuyEqualAmountHighScoreHoldTDay(Strategy) :
    def __init__(self, ranking_metric, score_cut=10, spare_amount=200000, hold_days=5, *args, **kwargs) :
        Strategy.__init__(self, *args, **kwargs)
        # selection-wise configuration
        self.ranking_metric = ranking_metric
        self.score_cut = score_cut
        self.spare_amount = spare_amount 
        self.hold_days = hold_days
    
    def _available_dates(self) :
        return self.available_dates[::self.hold_days]  + self.available_dates[-1:]
    
    def _select_snapshot(self, *args, **kwargs) :
        dt= args[0]
        selected = self.watching_list[self.watching_list[self.timestep] == dt] 
        return selected

    def _select_champion(self, snapshot) :
        selected = snapshot[snapshot[self.ranking_metric]>self.score_cut]
        return selected

    def _sell(self, snapshot, champion, dt, *args, **kwargs) :
        # Define the stocks in holding but not in champion is possible to be sold.
        tosell = set(self.holdings.current.keys()) - set(champion[self.key])
        for s in tosell :
            try :
                p = snapshot.loc[snapshot[self.key]==s, self.price].tolist()[0]
                sh = self.holdings.current[s]
                self.verboseprint('{} sell {} shares of stock {} at price {}'.format(str(dt)[:10], sh, s, p))
                self.holdings.sell(s, dt, sh, p)
            except Exception as e:
                print(repr(e))

    def _buy(self, snapshot, champion, dt, *args, **kwargs) :
        # Define the stocks in champion is possible to be bought.
        tobuy = set(champion[self.key]) - set(self.holdings.current.keys())
        for s in tobuy :
            try :
                p = snapshot.loc[snapshot[self.key]==s, self.price].tolist()[0]
                sh = self.spare_amount // (p*100)
                
                self.verboseprint('{} buy {} shares of stock {} at price {}'.format(str(dt)[:10], sh, s, p))
                
                self.holdings.buy(s, dt, sh, p)
            except Exception as e:
                print(repr(e))



class BuyHighSellLow(Strategy) :
    def __init__(self, ranking_metric, high_cut=0.9, low_cut=0.1, 
        hold_days=5, look_back_days=0, n_days=3, *args, **kwargs) :
        Strategy.__init__(self, *args, **kwargs)
        # selection-wise configuration
        self.ranking_metric = ranking_metric
        self.high_cut = high_cut
        self.low_cut = low_cut
        # self.spare_amount = spare_amount 
        self.hold_days = hold_days
        self.look_back_days = look_back_days
        self.n_days = n_days

    def _available_dates(self) :
        return self.available_dates[::self.hold_days]  + self.available_dates[-1:]

    def _sell_all(self, snapshot, dt, *args, **kwargs):
        return 

    def _select_snapshot(self, *args, **kwargs) :
        dt= args[0]
        
        idx = self.available_dates.index(dt)
        start = idx - self.look_back_days if idx >= self.look_back_days else 0
        end = idx +1 +1 # we calc the score after market closing, so we can only place any order in the next day.
        dates = self.available_dates[start:end]

        snaps = self.watching_list[self.watching_list[self.timestep].isin(dates)]

        return snaps

    def _select_champion(self, snapshot, *args, **kwargs) :
        '''
        Parameters
        --------------
        snapshot: a DataFrame generated by _select_snapshot method.
        Return
        ---------------
        Must be a DataFrame containing the champion at current dt. The champion can be generated from current snapshot or from current holdings.
        '''
        
        # new champion
        cur = snapshot[self.timestep].max()
        # filter 1: current score is larger than score cut.
        cond1 = snapshot[
            (snapshot[self.timestep] == cur) & 
            (snapshot[self.ranking_metric] >= self.high_cut) & 
            (snapshot[self.key].str[:5]!='SH688')
        ]
        # filter 2: no previous score is larger than score cut.
        cond2 = snapshot[
            (snapshot[self.timestep] < cur) & 
            (snapshot[self.ranking_metric] < self.high_cut) & 
            (snapshot[self.key].str[:5]!='SH688')
        ]
        champ = set(cond1[self.key]) & set(cond2[self.key])

        # high_cnt = snapshot[snapshot[self.ranking_metric]>self.score_cut].groupby(self.key)[self.ranking_metric].count()
        # high_cnt.name = 'cnt'
        # high_cnt = high_cnt.reset_index()
        # champ = high_cnt[high_cnt['cnt']>self.n_days]

        # KEEP current holding if they do NOT trigger exclusion condition
        # filter 3: current score is larger than score cut
        cond3 = snapshot[
            (snapshot[self.timestep] == cur) & 
            (snapshot[self.ranking_metric] >= self.low_cut) & # keep them if their score is still larger than low_cut
            (snapshot[self.key].isin(self.holdings.current.keys()))
        ]
        champ = champ | set(cond3[self.key])

        return pd.Series(list(champ), name=self.key).to_frame()