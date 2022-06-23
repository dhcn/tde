#!/usr/bin/env python
'''
High-frequency Tick Data Analysis Dashboard
Version: 0.2.3b
Development Env: Python 3.8
'''
# add timestamp:trade_count data display
# add timestamp:trade_size data display
import copy
import signal
import sys
from datetime import datetime, timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import json
import pandas as pd
from decimal import Decimal

from plotly import colors
from plotly.subplots import make_subplots

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

'''
dcc.Interval(
            id='interval-component',
            interval=1*100, # in milliseconds
            n_intervals=0
        )
'''
app.layout = html.Div([
    dcc.Graph(id='had-graph'),
    html.Span(["Step_Count: ",
              dcc.Input(id='my-input', value='10', type='text')]),
    html.Button('Continue', id='show-next'),

])

# Please contact me,if you need high-frequency data like this.
f = open("./data/OkexSubscriber2020-05-24","r")


#buys=[]
#sells=[]
#display_lob=[]
#trades = []
#best_asks=[]
#best_bids=[]
#--------
lob_df={}
asks_df ={}
bestasks_df={}
bestbids_df={}
best_ask=[0]
best_bid=[0]
bids_df ={}
trades_df ={}
buys_df={}
sells_df={}
zerobids_df={}
zeroasks_df={}
timestamp =""
asks ={}
bids ={}
buy_color=colors.qualitative.D3[3]
sell_color=colors.qualitative.D3[2]
ask_color=colors.qualitative.D3[1]
bid_color=colors.qualitative.D3[0]


def show_fig():
    global asks_df
    global bids_df
    global bestasks_df
    global bestbids_df
    global trades_df
    global buys_df
    global sells_df
    global zerobids_df
    global zeroasks_df
    global timestamp
    global best_ask
    global best_bid
    #print(timestamp)
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.01,
        specs=[[{"type": "bar"}],[{"type": "scatter"}],[{"type": "bar"}]]
    )

    start_time = timestamp-timedelta(seconds=10)
    bestasks_df=bestasks_df.loc[bestasks_df["timestamp"]>=start_time]
    bestbids_df = bestbids_df.loc[bestbids_df["timestamp"] >= start_time]
    trades_df = trades_df.loc[trades_df["timestamp"] >= start_time]
    sells_df = sells_df.loc[sells_df["timestamp"] >= start_time]
    buys_df = buys_df.loc[buys_df["timestamp"] >= start_time]
    zerobids_df = zerobids_df.loc[zerobids_df["timestamp"] >= start_time]
    zeroasks_df = zeroasks_df.loc[zeroasks_df["timestamp"] >= start_time]
    #print(zeroasks_df)
    #print(zerobids_df)

    fig.add_bar(x=asks_df["price"],y=asks_df["volume"],marker_color=asks_df["color"],row=1,col=1)
    fig.add_scatter(x=asks_df["price"],y=asks_df["volume"],marker_color=asks_df["color"],row=1,col=1,
                    fill='tozeroy', fillcolor=ask_color,
                    line_color=ask_color,
                    mode='markers+lines')
    fig.add_bar(x=bids_df["price"], y=bids_df["volume"], marker_color=bids_df["color"], row=1, col=1)
    fig.add_scatter(x=bids_df["price"], y=bids_df["volume"], marker_color=bids_df["color"], row=1, col=1,
                    line_color=bid_color,
                    fill='tozeroy', fillcolor=bid_color,
                    mode='markers+lines')



    fig.add_scatter(x=bestasks_df["timestamp"], y=bestasks_df["price"], row=2, col=1, y0=0,
                    line_color=ask_color,
                    text=bestasks_df["volume"],
                    marker_color=bestasks_df["color"],mode='lines')
    fig.add_scatter(x=bestbids_df["timestamp"], y=bestbids_df["price"], row=2, col=1, y0=0,
                    line_color=bid_color,
                    text=bestbids_df["volume"],
                    marker_color=bestbids_df["color"],mode='lines')

    fig.add_scatter(x=zerobids_df["timestamp"], y=zerobids_df["price"], row=2, col=1, y0=0,
                    text=zerobids_df["volume"],
                    marker_color=zerobids_df["color"], mode='markers')
    fig.add_scatter(x=zeroasks_df["timestamp"], y=zeroasks_df["price"], row=2, col=1, y0=0,
                    text=zeroasks_df["volume"],
                    marker_color=zeroasks_df["color"], mode='markers')


    #print(trades_df)
    fig.add_scatter(x=trades_df["timestamp"], y=trades_df["price"],text=trades_df['size'],row=2, col=1,
                    marker_color=trades_df["color"],
                    line_color=colors.qualitative.Light24[13],
                    y0=0,mode='markers+lines')

    #fig.add_bar(x=buys_df["timestamp"], y=-1*buys_df["size"], marker_color=buys_df["color"], row=3, col=1)
    #fig.add_bar(x=sells_df["timestamp"], y=sells_df["size"], marker_color=sells_df["color"], row=3, col=1)

    fig.add_scatter(x=buys_df["timestamp"],y=buys_df["size"],fill='tozeroy',fillcolor=buy_color,
                    marker_color=buys_df["color"],
                    line_color =buy_color,
                    row=3,col=1,mode='markers+lines')
    fig.add_scatter(x=sells_df["timestamp"], y=-1*sells_df["size"], fill='tozeroy', fillcolor=sell_color,
                    marker_color=sells_df["color"],
                    line_color=sell_color,
                    row=3, col=1,mode='markers+lines')

    fig.update_layout(
        height=900,
        showlegend=False,
        title_text=timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f"),
    )
    return fig
#@app.callback(Output('had-graph', 'figure'),
#              Input('interval-component', 'n_intervals'))
@app.callback(
    Output('had-graph', 'figure'),
    Input(component_id='show-next', component_property='n_clicks'),
    Input(component_id='my-input', component_property='value'))
def update_output(n_clicks,value):
    #print(n_clicks)
    if n_clicks is None:
        raise PreventUpdate
    #global display_lob

    #global best_asks
    #global best_bids
    #global buys
    #global sells

    global asks
    global bids
    global timestamp
    global lob_df
    global asks_df
    global bids_df
    global bestasks_df
    global bestbids_df
    global best_ask
    global best_bid
    global trades_df
    global buys_df
    global sells_df
    global zerobids_df
    global zeroasks_df
    global step_count

    display_count=60
    step_count = int(value)


    while True:
        line = f.readline()
        print(line)
        line_obj = json.loads(line)
        #print(line_obj)
        if "event" in line_obj and line_obj["event"] == "subscribe":
            asks_df= pd.DataFrame(columns=['price', 'volume','undefined','count','color'])
            bids_df = pd.DataFrame(columns=['price', 'volume', 'undefined', 'count', 'color'])
            zeroasks_df=pd.DataFrame(columns=['price', 'volume', 'undefined', 'count', 'color', "timestamp"])
            zerobids_df=pd.DataFrame(columns=['price', 'volume', 'undefined', 'count', 'color', "timestamp"])
            bestasks_df = pd.DataFrame(columns=['price', 'volume', 'undefined', 'count', 'color', "timestamp"])
            bestbids_df = pd.DataFrame(columns=['price', 'volume', 'undefined', 'count', 'color', "timestamp"])
            trades_df = pd.DataFrame(columns=['side', 'trade_id', 'price', 'size', 'instrument', "timestamp", "color"])
            buys_df = pd.DataFrame(columns=['side', 'trade_id', 'price', 'size', 'instrument', "timestamp", "color"])
            sells_df = pd.DataFrame(columns=['side', 'trade_id', 'price', 'size', 'instrument', "timestamp", "color"])

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
            #display_lob =[]

            for bid in bid_list:
                for i in range(3):
                    bid[i]=Decimal(bid[i])
                bid.append(bid_color)
                if int(bid[3])==0:
                    if Decimal(bid[0]) in bids:
                        del bids[Decimal(bid[0])]
                    else:
                        if  bid[0]<best_ask[0]+5*(best_ask[0]-best_bid[0]) and bid[0]>best_ask[0]-5*(best_ask[0]-best_bid[0]):
                            #print(bid[0])
                            #print(best_ask[0]-10*(best_ask[0]-best_bid[0]))
                            bid.append(timestamp)
                            zerobids_df = zerobids_df.append(pd.DataFrame([bid],columns=['price', 'volume', 'undefined',
                                                                                     'count','color', "timestamp"]))
                else:
                    bids[bid[0]] = bid
            if len(bids)<display_count:
                start= 0-len(bids)
            else:
                start = 0-display_count
            sorted_bids = sorted(bids)
            display_bids=[]
            for i in range(start,0):
                display_bids.append(bids[sorted_bids[i]])

            bids_df = pd.DataFrame(display_bids, columns=['price', 'volume', 'undefined', 'count', 'color'])

            for ask in ask_list:
                for i in range(3):
                    ask[i]=Decimal(ask[i])
                ask.append(ask_color)
                if int(ask[3])==0:
                    if Decimal(ask[0]) in asks:
                        del asks[Decimal(ask[0])]
                    else:
                        if  ask[0] > (best_bid[0] - 5 * (best_ask[0] - best_bid[0])) and ask[0] < (best_bid[0] + 5 * (best_ask[0] - best_bid[0])):
                            ask.append(timestamp)
                            zeroasks_df = zeroasks_df.append(pd.DataFrame([ask], columns=['price', 'volume', 'undefined',
                                                                                      'count', 'color', "timestamp"]))

                else:
                    asks[ask[0]] = ask

            if len(asks)<display_count:
                start= len(asks)
            else:
                start = display_count

            sorted_asks = sorted(asks)
            display_asks=[]
            for i in range(0,start):
                display_asks.append(asks[sorted_asks[i]])

            asks_df = pd.DataFrame(display_asks, columns=['price', 'volume', 'undefined', 'count', 'color'])

            best_ask=copy.deepcopy(asks[sorted_asks[0]])
            # print(best_ask)
            best_ask.append(data["timestamp"])
            best_bid=copy.deepcopy(bids[sorted_bids[-1]])
            best_bid.append(data["timestamp"])
            bestasks_df=bestasks_df.append(pd.DataFrame([best_ask],columns=['price', 'volume','undefined','count','color',"timestamp"]))
            bestbids_df=bestbids_df.append(pd.DataFrame([best_bid],columns=['price', 'volume','undefined','count','color',"timestamp"]))
            # print(best_bid)


            if step_count<=0:
                break
            else:
                step_count=step_count-1
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
            data = line_obj["data"][0]
            time_str=data["timestamp"].replace("Z","000")
            data["timestamp"]= datetime.strptime(time_str,"%Y-%m-%dT%H:%M:%S.%f")
            data["price"]=Decimal(data["price"])
            data["size"] = float(data["size"])
            if data["side"]=="buy":
                data["color"]=buy_color
                buys_df=buys_df.append(pd.DataFrame([data],columns=['side', 'trade_id', 'price', 'size', 'instrument', "timestamp", "color"]))
                #buys.append(data)
            else:
                data["color"] = sell_color
                sells_df=sells_df.append(pd.DataFrame([data],
                                            columns=['side', 'trade_id', 'price', 'size', 'instrument', "timestamp",
                                                     "color"]))
                #sells.append(data)

            trades_df=trades_df.append(pd.DataFrame([data],columns=['side', 'trade_id', 'price', 'size', 'instrument', "timestamp", "color"]))

            # print(trades_df)
            #trades.append(data)
            timestamp = data["timestamp"]
            continue
        else:
            continue
    return show_fig()

def exit(signum, frame):
    print('You choose to stop me!')
    sys.exit(0)
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, exit)
    app.run_server(debug=True)