import pandas as pd
from trnsim.strategy import *

if __name__ == '__main__' :
    data = pd.read_csv('./data/simulation_2022f.csv', sep=',')
    hold_days=1
    look_back_days=5
    high_cut=0.99
    low_cut=0.6
    spare_amount=300000
    max_portion=0.5
    fmc = ['XL', 'LG', 'SM']
    strgy = BuyHighSellLow(
        watching_list=data[data['model'].str[:2].isin(fmc)], 
        begin='2022-01-01', end='2023-12-30', 
        ranking_metric='score', high_cut=high_cut, low_cut=low_cut , verbose=0, funding=spare_amount,
        hold_days=hold_days, look_back_days=10, max_portion=max_portion
    )
    output1 = strgy.run()

    print(output1)
    result = pd.DataFrame.from_dict(strgy.stats)
    # result.plot()
    result.to_csv('net_{}_{}_{}_{}_{}.csv'.format('2022f300k', ''.join(fmc), high_cut, low_cut, max_portion), index=None)
    
    # output1 = BuyHighSellLow(
    #     watching_list=data[data['model'].str[:2]=='MD'],  begin='2022-12-01', end='2023-12-31', 
    #     ranking_metric='score', high_cut=0.99, low_cut=0.7, verbose=1, spare_amount=spare_amount,
    #     hold_days=hold_days, look_back_days=look_back_days
    # ).run()

    # print(output1)