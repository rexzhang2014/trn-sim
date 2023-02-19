import pandas as pd
from trnsim.strategy import *

if __name__ == '__main__' :
    data = pd.read_csv('./data/simulation_combine.csv', sep=',')
    hold_days=1
    topk=1
    spare_amount=10000000

    output1 = BuyEqualAmountTopKAndHoldTDay(
        watching_list=data, begin='2022-12-01', end='2022-12-31', ranking_metric='score_INC', topk=topk, verbose=1, spare_amount=spare_amount,
        hold_days=hold_days
    ).run()

    print(output1)
