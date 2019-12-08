import pandas as pd
import numpy as np

data = pd.read_csv("ita1.csv", names=['bid_vol', 'ask_vol', 'best_bid', 'best_ask', 'best_bid_size', 'best_ask_size', 'bid_size_3', 'ask_size_3', 'bid_size_5', 'ask_size_5', 'bid_size_10', 'ask_size_10', 'sell_size_100', 'buy_size_100'])
print(data.corr())
