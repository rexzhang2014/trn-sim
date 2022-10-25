import pandas as pd
from trnsim.strategy import *

if __name__ == '__main__' :
    # data = pd.read_csv('./data/sim_cyb_L20D50G50.csv', sep=',')
    data = pd.read_csv('./data/sim_cyb_v3.0.csv', sep=',')

    hold_days=5
    topk=1
    spare_amount=10000

    output1 = BuyEqualAmountTopKAndHoldTDay(
        watching_list=data, begin='2021-10-01', end='2021-11-18', ranking_metric='score', topk=topk, verbose=1, spare_amount=spare_amount,
        hold_days=hold_days
    ).run()

    print(output1)

    # output2 = BuyEqualAmountTopKAndHoldTDay(
    #     watching_list=data, begin='2020-06-01', end='2020-06-30', ranking_metric='score', topk=topk, verbose=0, spare_amount=spare_amount,
    #     hold_days=hold_days
    # ).run()

    # print(output2)