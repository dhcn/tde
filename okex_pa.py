#%%volume imbalance time_str
#!/usr/bin/env python
'''
Binan trade price analysis
Version: 0.1b
Development Env: Python 3.8
'''
# add timestamp:trade_count data display
# add timestamp:trade_size data display
import copy
import signal
import sys
from datetime import datetime, timedelta

import json
import pandas as pd
from decimal import Decimal





# Please contact me,if you need high-frequency data like this.
f = open("./data/OkexSubscriber2020-05-24","r")


asks=[]
bids=[]
sell_trades_count={}
buy_trades_count={}


def ana_data():
    global asks
    global bids
    global sell_trades_count
    global buy_trades_count
    for line in f:
        #print(line)
        line_obj = json.loads(line)
        #print(line_obj)
        if "event" in line_obj and line_obj["event"] == "subscribe":
            asks =set()
            bids =set()

            continue
        elif "table" in line_obj and line_obj["table"] == "spot/depth_l2_tbt":
            '''
            "data": [
                {
                    "instrument_id": "BTC-USDT",
                    "asks": [
                        [
                            "9256.8",
                            "1.165",
                            "0",
                            "3"
                        ],
                        [
                            "9257.4",
                            "0.24",
                            "0",
                            "1"
                        ],
                        [
                            "9261.7",
                            "0.01193377",
                            "0",
                            "1"
                        ]
                    ],
                    "bids": [
                        [
                            "9252.1",
                            "0.001",
                            "0",
                            "1"
                        ]
                    ],
                    "timestamp": "2020-05-24T08:17:45.718Z",
                    "checksum": 55642953
                }
            ]
            '''
            data = line_obj["data"][0]
            ask_list = data["asks"]
            bid_list = data["bids"]

            time_str = data["timestamp"].replace("Z", "000")
            data["timestamp"] = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f")
            timestamp = data["timestamp"]
            #print("Tick time:%s"%time_str)

            for bid in bid_list:
                for i in range(3):
                    bid[i]=Decimal(bid[i])
                if int(bid[3])==0:
                    if Decimal(bid[0]) in bids:
                        bids.remove(Decimal(bid[0]))
                    #else:
                        #print("Exception")
                else:
                    bids.add(Decimal(bid[0]))

            for ask in ask_list:

                if int(ask[3])==0:
                    if Decimal(ask[0]) in asks:
                        asks.remove(Decimal(ask[0]))
                    #else:
                    #    print("Exception")

                else:
                    asks.add(Decimal(ask[0]))
            sorted_asks = sorted(asks)

        elif "table" in line_obj and line_obj["table"] == "spot/trade" :
            '''
            {
                "table": "spot/trade",
                "data": [
                    {
                        "side": "sell",
                        "trade_id": "82354817",
                        "price": "9253.5",
                        "size": "0.00000007",
                        "instrument_id": "BTC-USDT",
                        "timestamp": "2020-05-24T08:17:41.806Z"
                    }
                ]
            }
            '''
            if len(line_obj["data"])>1:
                print("trade lenth error>1!!!!!!!!!!!!!!!!!!!!!!")
            data = line_obj["data"][0]
            time_str=data["timestamp"].replace("Z","000")
            #print("Trade time:%s" % time_str)
            data["timestamp"]= datetime.strptime(time_str,"%Y-%m-%dT%H:%M:%S.%f")
            trade_price=Decimal(data["price"])
            trade_side =data["side"]

            sorted_bids = sorted(bids)
            sorted_asks = sorted(asks)
            sorted_bids.reverse()
            #print(sorted_bids)
            #print(sorted_asks)
            if len(asks)==0:
                continue
            if trade_side=="sell":
                lob_level = int(((sorted_bids[0]-trade_price)/Decimal(0.1)).quantize(Decimal('0')))
                if lob_level in sell_trades_count:
                    sell_trades_count[lob_level] = sell_trades_count[lob_level] + 1
                else:
                    sell_trades_count[lob_level] = 0
            elif  trade_side=="buy":
                lob_level = int(((trade_price-sorted_asks[0])/Decimal(0.1)).quantize(Decimal('0')))
                if lob_level in buy_trades_count:
                    buy_trades_count[lob_level] = buy_trades_count[lob_level] + 1
                else:
                    buy_trades_count[lob_level] = 0
            else:
                print("trade side error")
            '''
            if lob_level<0:
                print(sorted_bids)
                print(sorted_asks)
                print(trade_price)
                print(trade_side)
            '''
            #print(buy_trades_count)
            #print(sell_trades_count)

            continue
        else:
            continue

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
    print(json.dumps(sell_trades_count))
    print(sell_all_count)
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