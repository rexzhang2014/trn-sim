import pandas as pd
from trnsim.strategy import *

if __name__ == '__main__' :
    data = pd.read_csv('./data/simulation_2212_2302.csv', sep=',')
    hold_days=1
    look_back_days=10
    high_cut=0.95
    low_cut=0.2
    n_days = 1
    spare_amount=10000000

    # output1 = BuyEqualAmountTopKAndHoldTDay(
    #     watching_list=data[data['model'].str[:2]=='XL'], begin='2022-12-01', end='2023-12-31', 
    #     ranking_metric='score', topk=topk, verbose=0, spare_amount=spare_amount,
    #     hold_days=hold_days
    # ).run()

    # print(output1)

    # output1 = BuyEqualAmountTopKAndHoldTDay(
    #     watching_list=data[data['model'].str[:2]=='LG'], begin='2022-12-01', end='2023-12-31', 
    #     ranking_metric='score', topk=topk, verbose=0, spare_amount=spare_amount,
    #     hold_days=hold_days
    # ).run()

    # print(output1)

    # output1 = BuyEqualAmountTopKAndHoldTDay(
    #     watching_list=data[data['model'].str[:2]=='MD'], begin='2022-12-01', end='2023-12-31', 
    #     ranking_metric='score', topk=topk, verbose=0, spare_amount=spare_amount,
    #     hold_days=hold_days
    # ).run()

    # print(output1)


    output1 = BuyHighSellLow(
        watching_list=data[data['model'].str[:2]=='XL'], begin='2022-12-01', end='2023-12-31', 
        ranking_metric='score', high_cut=0.99, low_cut=0.8, verbose=1, spare_amount=spare_amount,
        hold_days=hold_days, look_back_days=look_back_days
    ).run()

    print(output1)
    
    
    output1 = BuyHighSellLow(
        watching_list=data[data['model'].str[:2]=='LG'], begin='2023-01-01', end='2023-12-31', 
        ranking_metric='score', high_cut=0.995, low_cut=0.8, verbose=1, spare_amount=spare_amount,
        hold_days=hold_days, look_back_days=look_back_days
    ).run()

    print(output1)
    
    # output1 = BuyHighSellLow(
    #     watching_list=data[data['model'].str[:2]=='MD'],  begin='2022-12-01', end='2023-12-31', 
    #     ranking_metric='score', high_cut=0.99, low_cut=0.7, verbose=1, spare_amount=spare_amount,
    #     hold_days=hold_days, look_back_days=look_back_days
    # ).run()

    # print(output1)