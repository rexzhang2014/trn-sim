from .base import *

class BuyEqualAmountTopKAndHoldTDay(Strategy) :
    def __init__(self, ranking_metric, topk=10, spare_amount=200000, hold_days=5, *args, **kwargs) :
        Strategy.__init__(self, *args, **kwargs)
        # selection-wise configuration
        self.ranking_metric = ranking_metric
        self.topk = topk
        self.spare_amount = spare_amount 
        self.hold_days = hold_days
        
    def run(self, *args, **kwargs) :
        for dt in self.available_dates[::self.hold_days]  + self.available_dates[-1:]:
            snapshot = self.watching_list[self.watching_list['date'] == dt] 
            selected = snapshot.sort_values(self.ranking_metric, ascending=False).head(self.topk)
            
            # 0. at last day, assume we clear the holdings
            if dt == self.available_dates[-1] :
                tosell = set(self.holdings.current.keys())
                for s in tosell :
                    try :
                        p = snapshot.loc[snapshot['symbol']==s, 'close'].tolist()[0]
                        sh = self.holdings.current[s]
                        self.verboseprint('{} sell {} shares of stock {} at price {}'.format(str(dt)[:10], sh, s, p))
                        self.holdings.sell(s, dt, sh, p)
                    except Exception as e:
                        print(repr(e))
                        
                break
                
            # 1. sell holdings that are out of topk
            tosell = set(self.holdings.current.keys()) - set(selected['symbol'])
#             self.verboseprint(selected)
            for s in tosell :
                try :

                    p = snapshot.loc[snapshot['symbol']==s, 'close'].tolist()[0]
                    sh = self.holdings.current[s]
                    self.verboseprint('{} sell {} shares of stock {} at price {}'.format(str(dt)[:10], sh, s, p))
                    self.holdings.sell(s, dt, sh, p)
                except Exception as e:
                    print(repr(e))
                
            # holding.buy('SH600000', '2020-05-01', 100, 5,)
            # 2. buy topk on that day with today's close price (assume we are able to do this in next day, before next closing.)
            tobuy = set(selected['symbol']) - set(self.holdings.current.keys())
            
            for s in tobuy :
                try :
                    p = snapshot.loc[snapshot['symbol']==s, 'close'].tolist()[0]
                    sh = self.spare_amount // (p*100)
                    
                    self.verboseprint('{} buy {} shares of stock {} at price {}'.format(str(dt)[:10], sh, s, p))
                    
                    self.holdings.buy(s, dt, sh, p)
                except Exception as e:
                    print(repr(e))
                    
            self.verboseprint(self.holdings.current)
                    
            self.verboseprint('trading gain: {} , gain: {}'.format(self.holdings.trading_gain(self.begin, dt), self.holdings.gain(dt)))
            
        
        output = {
            'buy_amount' : self.holdings.buy_amount(self.begin, self.end), 
            'sell_amount' : self.holdings.sell_amount(self.begin, self.end), 
            'hold_amount' : self.holdings.holding_amount(self.begin, self.end), 
            'current' : self.holdings.current, 
            'trading_gain' : self.holdings.trading_gain(self.begin, self.end), 
            'gain' : self.holdings.gain(self.end), 
            'txn_cnt' : self.holdings.txn_cnt(self.begin, self.end),
            
        }
        return output
                        