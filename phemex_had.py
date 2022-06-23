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
              dcc.Input(id='my-input', value='1', type='text')]),
    html.Button('Continue', id='show-next'),

])

# Please contact me,if you need high-frequency data like this.
f = open("./data/PhemexSubscriber2021-06-07","r")


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

trades_df = pd.DataFrame(columns=['price', 'size','timestamp', "color", "side"])
buys_df = pd.DataFrame(columns=['price', 'size','timestamp', "color", "side"])
sells_df = pd.DataFrame(columns=['price', 'size','timestamp', "color", "side"])

#zerobids_df={}
#zeroasks_df={}
timestamp =""
asks ={}
bids ={}
buy_color=colors.qualitative.D3[3]
sell_color=colors.qualitative.D3[2]
ask_color=colors.qualitative.D3[1]
bid_color=colors.qualitative.D3[0]

def microseconds_to_datetime(timee6):
    return datetime(1970, 1, 1)+timedelta(microseconds=timee6)

def timestamp_to_datetime(timestapm_str):
    time_str = timestapm_str.replace("Z", "000")
    return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f")
def show_fig():
    global asks_df
    global bids_df
    global bestasks_df
    global bestbids_df
    global trades_df
    global buys_df
    global sells_df
    #global zerobids_df
    #global zeroasks_df
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

    start_time = timestamp-timedelta(seconds=20)
    bestasks_df= bestasks_df.loc[bestasks_df["timestamp"]>=start_time]
    bestbids_df = bestbids_df.loc[bestbids_df["timestamp"] >= start_time]
    trades_df = trades_df.loc[trades_df["timestamp"] >= start_time]
    sells_df = sells_df.loc[sells_df["timestamp"] >= start_time]
    buys_df = buys_df.loc[buys_df["timestamp"] >= start_time]
    #zerobids_df = zerobids_df.loc[zerobids_df["timestamp"] >= start_time]
    #zeroasks_df = zeroasks_df.loc[zeroasks_df["timestamp"] >= start_time]
    #print(zeroasks_df)
    #print(zerobids_df)

    fig.add_bar(x=asks_df["price"],y=asks_df["size"],marker_color=asks_df["color"],row=1,col=1)
    fig.add_scatter(x=asks_df["price"],y=asks_df["size"],marker_color=asks_df["color"],row=1,col=1,
                    fill='tozeroy', fillcolor=ask_color,
                    line_color=ask_color,
                    mode='markers+lines')
    fig.add_bar(x=bids_df["price"], y=bids_df["size"], marker_color=bids_df["color"], row=1, col=1)
    fig.add_scatter(x=bids_df["price"], y=bids_df["size"], marker_color=bids_df["color"], row=1, col=1,
                    line_color=bid_color,
                    fill='tozeroy', fillcolor=bid_color,
                    mode='markers+lines')



    fig.add_scatter(x=bestasks_df["timestamp"], y=bestasks_df["price"], row=2, col=1, y0=0,
                    line_color=ask_color,
                    text=bestasks_df["size"],
                    marker_color=bestasks_df["color"],mode='markers+lines')
    fig.add_scatter(x=bestbids_df["timestamp"], y=bestbids_df["price"], row=2, col=1, y0=0,
                    line_color=bid_color,
                    text=bestbids_df["size"],
                    marker_color=bestbids_df["color"],mode='markers+lines')

    #print(trades_df)
    fig.add_scatter(x=trades_df["timestamp"], y=trades_df["price"],text=trades_df['size'],row=2, col=1,
                    marker_color=trades_df["color"],
                    line_color=colors.qualitative.Light24[13],
                    y0=0,mode='markers+lines')

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
    #global zerobids_df
    #global zeroasks_df
    global step_count

    display_count=60
    step_count = int(value)


    while True:
        line = f.readline()
        #print(line)
        line_obj = json.loads(line)
        #print(line_obj)
        if "book" in line_obj:
            if line_obj["type"] == "snapshot":
                '''
                {
                    "book": {
                        "asks": [
                            [
                                593115000,
                                507601
                            ],
                            [
                                593125000,
                                100
                            ]
                        ],
                        "bids": [
                            [
                                593110000,
                                1275884
                            ],
                            [
                                593080000,
                                532665
                            ]
                        ]
                    },
                    "depth": 30,
                    "sequence": 6555125961,
                    "symbol": "BTCUSD",
                    "timestamp": 1617455129498811000,
                    "type": "snapshot"
                }
                '''

                asks_df= pd.DataFrame(columns=['price', 'size', 'color'])
                bids_df = pd.DataFrame(columns=['price', 'size', 'color'])
                bestasks_df = pd.DataFrame(columns=['price', 'size', 'color', "timestamp"])
                bestbids_df = pd.DataFrame(columns=['price', 'size', 'color', "timestamp"])

                data = line_obj["book"]
                time_str = line_obj["timestamp"]
                data["timestamp"] = microseconds_to_datetime(int(time_str)/1000)
                timestamp = data["timestamp"]
                # display_lob =[]
                for ask in data["asks"]:
                    ask[0]=Decimal(ask[0])
                    ask[1] = Decimal(ask[1])
                    ask.append(ask_color)
                    asks[ask[0]]=ask
                for bid in data["bids"]:
                    bid[0] = Decimal(bid[0])
                    bid[1] = Decimal(bid[1])
                    bid.append(bid_color)
                    bids[bid[0]] = bid

            elif line_obj["type"] == "incremental":
                '''
                {
                    "book": {
                        "asks": [
                            [
                                593160000,
                                199
                            ]
                        ],
                        "bids": [
                            [
                                593080000,
                                0
                            ],
                            [
                                592910000,
                                13268
                            ]
                        ]
                    },
                    "depth": 30,
                    "sequence": 6555126603,
                    "symbol": "BTCUSD",
                    "timestamp": 1617455133335040800,
                    "type": "incremental"
                }
                '''
                data = line_obj["book"]
                time_str = line_obj["timestamp"]
                data["timestamp"] = microseconds_to_datetime(int(time_str)/1000)
                print(microseconds_to_datetime(int(time_str)/1000))
                timestamp = data["timestamp"]
                # display_lob =[]
                for ask in data["asks"]:
                    ask[0]=Decimal(ask[0])
                    ask[1] = Decimal(ask[1])
                    if ask[1]==Decimal(0):
                        if ask[0] in asks:
                            del asks[ask[0]]
                        else:
                            print("{}  ask  not  found in asks on {}".format(ask,timestamp))
                    else:
                        ask.append(ask_color)
                        asks[ask[0]]=ask
                for bid in data["bids"]:
                    bid[0] = Decimal(bid[0])
                    bid[1] = Decimal(bid[1])
                    if bid[1]==Decimal(0):
                        if bid[0] in bids:
                            del bids[bid[0]]
                        else:
                            print("{}  bid  not  found in bids on {}".format(bid,timestamp))
                    else:
                        bid.append(bid_color)
                        bids[bid[0]] = bid

            '''
            For lob display df generate
            '''

            if len(bids) < display_count:
                start = 0 - len(bids)
            else:
                start = 0 - display_count
            sorted_bids = sorted(bids)
            display_bids = []
            for i in range(start, 0):
                display_bids.append(bids[sorted_bids[i]])

            bids_df = pd.DataFrame(display_bids, columns=['price', 'size', 'color'])

            if len(asks) < display_count:
                start = len(asks)
            else:
                start = display_count

            sorted_asks = sorted(asks)
            display_asks = []
            for i in range(0, start):
                display_asks.append(asks[sorted_asks[i]])

            asks_df = pd.DataFrame(display_asks, columns=['price', 'size', 'color'])

            best_ask = copy.deepcopy(asks[sorted_asks[0]])
            best_ask.append(timestamp)

            best_bid = copy.deepcopy(bids[sorted_bids[-1]])
            best_bid.append(timestamp)

            bestasks_df = bestasks_df.append(
                pd.DataFrame([best_ask], columns=['price', 'size', 'color', "timestamp"]))
            bestbids_df = bestbids_df.append(
                pd.DataFrame([best_bid], columns=['price', 'size', 'color', "timestamp"]))
            # print(best_bid)
            #print("step_count check")
            if step_count <= 1:
                break
            else:
                step_count = step_count - 1

        elif "trades" in line_obj and line_obj["type"] == "incremental":
            '''
            {
                "sequence": 6555126166,
                "symbol": "BTCUSD",
                "trades": [
                    [
                        1617455129930468400,
                        "Buy",
                        593115000,
                        301
                    ]
                ],
                "type": "incremental"
            }
            '''
            data = line_obj["trades"]
            for trade_data in data:
                trade={}
                trade["timestamp"] = microseconds_to_datetime(int(trade_data[0])/1000)
                trade["price"]=Decimal(trade_data[2])
                trade["size"] = Decimal(trade_data[3])
                timestamp = trade["timestamp"]
                if trade_data[1]=="Buy":
                    trade["color"]=buy_color
                    trade["side"] = "Buy"
                    buys_df=buys_df.append(pd.DataFrame([trade],columns=['price', 'size',
                                                                         'timestamp', "color", "side"]))
                    #buys.append(data)
                elif trade_data[1]=="Sell":
                    trade["color"] = sell_color
                    trade["side"] = "Sell"
                    sells_df=sells_df.append(pd.DataFrame([trade],columns=['price', 'size',
                                                                         'timestamp', "color", "side"]))
                #sells.append(data)
                # print(trade)
                trades_df=trades_df.append(pd.DataFrame([trade],columns=['price', 'size',
                                                                         'timestamp', "color", "side"]))

            # print(trades_df)
            #trades.append(data)
            #print("step_count check")
            if step_count <= 1:
                break
            else:
                step_count = step_count - 1
        else:
            continue
    return show_fig()

def exit(signum, frame):
    print('You choose to stop me!')
    sys.exit(0)
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, exit)
    app.run_server(debug=True)