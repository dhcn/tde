#%%volume imbalance time_str
#!/usr/bin/env python
'''
Phemex trade price analysis
Version: 0.1b
Development Env: Python 3.8
book data和Trade data有乱序
'''
import sys
from datetime import datetime, timedelta

import json
from decimal import Decimal

from utils import microseconds_to_datetime

asks=[]
bids=[]
sell_trades_count={}
buy_trades_count={}

file_name = "./data/PhemexSubscriber2021-04-03"
def ana_data():
    global asks
    global bids
    global sell_trades_count
    global buy_trades_count
    best_ba=[]
    with open(file_name, "r") as f:
        for line in f:
            line_obj = json.loads(line)

            #print(line_obj)
            if "id" in line_obj and line_obj["id"] == 10071 and line_obj["result"]["status"]=="success":
                asks =set()
                bids =set()
                continue

            elif "book" in line_obj:
                '''
                {
                    "book": {
                        "asks": [
                            [
                                593360000,
                                600
                            ],
                            [
                                593455000,
                                0
                            ]
                        ],
                        "bids": []
                    },
                    "depth": 30,
                    "sequence": 6555126179,
                    "symbol": "BTCUSD",
                    "timestamp": 1617455130245972200,
                    "type": "incremental"
                }
                '''
                book_data = line_obj["book"]
                ask_list = book_data["asks"]
                bid_list = book_data["bids"]
                book_timestamp = microseconds_to_datetime(line_obj["timestamp"]/1000)

                for bid in bid_list:
                    price = int(bid[0])/1000
                    volume = int(bid[1])
                    if volume  == 0:
                        if price in bids:
                            bids.remove(price)
                        #else:
                            #print("Exception")
                    else:
                        bids.add(price)

                for ask in ask_list:
                    price = int(ask[0])/1000
                    volume = int(ask[1])
                    if volume==0:
                        if price in asks:
                            asks.remove(price)
                        #else:
                        #    print("Exception")

                    else:
                        asks.add(price)
                sorted_bids = sorted(bids)
                sorted_asks = sorted(asks)
                sorted_bids.reverse()
                best_bid = sorted_bids[0]
                best_ask = sorted_asks[0]
                best_ba.append([line_obj["timestamp"],best_bid,best_ask])
    with open(file_name, "r") as f:
        ba_index=0
        for line in f:
            line_obj = json.loads(line)

            if "trades" in line_obj and line_obj["type"] == "incremental":
                '''
                {
                    "sequence": 6555126190,
                    "symbol": "BTCUSD",
                    "trades": [
                        [
                            1617455131513057000,
                            "Sell",
                            593110000,
                            5
                        ]
                    ],
                    "type": "incremental"
                }
                '''
                trades = line_obj["trades"]

                for trade in trades:
                    trade_price = trade[2]/1000
                    trade_side  = trade[1]
                    trade_time = microseconds_to_datetime(trade[0]/1000)
                    trade_time_ns = trade[0]

                    while True:
                        lob_time1 = best_ba[ba_index][0]
                        lob_time2 = best_ba[ba_index+1][0]
                        best_bid = best_ba[ba_index][1]
                        best_ask = best_ba[ba_index][2]
                        if trade_time_ns<lob_time1:
                            break
                        elif trade_time_ns>=lob_time1 and trade_time_ns<lob_time2:

                            if trade_side=="Sell":
                                lob_level=(best_bid-trade_price)/5
                                #print("!!!!!")
                                #print(best_bid)
                                #print(trade_price)
                                if lob_level in sell_trades_count:
                                    sell_trades_count[lob_level] = sell_trades_count[lob_level] + 1
                                else:
                                    sell_trades_count[lob_level] = 0
                            elif trade_side=="Buy":
                                lob_level=(trade_price-best_ask)/5
                                if lob_level in buy_trades_count:
                                    buy_trades_count[lob_level] = buy_trades_count[lob_level] + 1
                                else:
                                    buy_trades_count[lob_level] = 0
                            break
                        elif trade_time_ns>=lob_time2:
                            ba_index=ba_index+1

                            continue
        print("end!!!!!!!!!!")

def output_trades_count():
    global buy_trades_count
    global sell_trades_count
    buy_all_count=sum(buy_trades_count.values())
    sell_all_count=sum(sell_trades_count.values())
    for key in buy_trades_count:
        prop = (buy_trades_count[key]/buy_all_count)*100
        buy_trades_count[key]=prop
    for key in sell_trades_count:
        prop = (sell_trades_count[key]/sell_all_count)*100
        sell_trades_count[key]=prop

    buy_trades_count = sorted(buy_trades_count.items(), key=lambda d: d[0], reverse=False)
    sell_trades_count = sorted(sell_trades_count.items(), key=lambda d: d[0], reverse=False)
    print(json.dumps(buy_trades_count))

    print(buy_all_count)
    print(sum([item[1] for item in buy_trades_count if item[0] >= 0]))
    print(json.dumps(sell_trades_count))

    print(sell_all_count)
    print(sum([item[1] for item in sell_trades_count if item[0] >= 0]))
    import plotly.express as px
    import plotly
    from plotly.subplots import make_subplots
    from plotly import colors
    fig = make_subplots(
        rows=1, cols=2,
        shared_xaxes=True,
        vertical_spacing=0.01,
        specs=[[{"type": "scatter"},{"type": "scatter"}]]
    )
    fig.add_scatter(x=[count[0] for count in buy_trades_count], y=[count[1] for count in buy_trades_count],row=1, col=1)
    fig.add_scatter(x=[count[0] for count in sell_trades_count], y=[count[1] for count in sell_trades_count],row=1, col=2)
    plotly.offline.plot(fig)
def exit(signum, frame):
    print('You choose to stop me!')
    sys.exit(0)
if __name__ == '__main__':
    ana_data()
    output_trades_count()