
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

if __name__ == '__main__' :
    data = pd.read_csv('./data/simulation_combine.csv', sep=',')
    hold_days=1
    topk=2
    spare_amount=10000000

    output1 = BuyEqualAmountTopKAndHoldTDay(
        watching_list=data, begin='2022-12-01', end='2023-02-20', ranking_metric='score_INC', topk=topk, verbose=1, spare_amount=spare_amount,
        hold_days=hold_days
    ).run()

    print(output1)
