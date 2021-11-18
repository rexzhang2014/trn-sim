import pandas as pd
from trnsim.strategy import *

if __name__ == '__main__' :
    data = pd.read_csv('./data/strategydata.csv', sep='|')

    hold_days=30
    topk=2
    spare_amount=300000

    output1 = BuyEqualAmountTopKAndHoldTDay(
        watching_list=data, begin='2020-05-01', end='2020-07-31', ranking_metric='score', topk=topk, verbose=1, spare_amount=spare_amount,
        hold_days=hold_days
    ).run()

    print(output1)

    output2 = BuyEqualAmountTopKAndHoldTDay(
        watching_list=data, begin='2020-06-01', end='2020-06-30', ranking_metric='score', topk=topk, verbose=0, spare_amount=spare_amount,
        hold_days=hold_days
    ).run()

    print(output2)