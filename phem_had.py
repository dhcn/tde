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
f = open("./data/PhemexSubscriber2021-04-03","r")


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

trades_df = pd.DataFrame(columns=['symbol', 'tick_direction', 'price', 'size',
                                  'timestamp', "trade_time_ms", "side","trade_id","color"])
buys_df = pd.DataFrame(columns=['symbol', 'tick_direction', 'price', 'size',
                                  'timestamp', "trade_time_ms", "side","trade_id","color"])
sells_df = pd.DataFrame(columns=['symbol', 'tick_direction', 'price', 'size',
                                  'timestamp', "trade_time_ms", "side","trade_id","color"])

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

    start_time = timestamp-timedelta(seconds=10)
    bestasks_df=bestasks_df.loc[bestasks_df["timestamp"]>=start_time]
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
                    marker_color=bestasks_df["color"],mode='lines')
    fig.add_scatter(x=bestbids_df["timestamp"], y=bestbids_df["price"], row=2, col=1, y0=0,
                    line_color=bid_color,
                    text=bestbids_df["size"],
                    marker_color=bestbids_df["color"],mode='lines')

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
    if n_clicks is None:
        raise PreventUpdate

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

    display_count=500
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

                asks_df= pd.DataFrame(columns=['price', 'symbol', 'id', 'side', 'size','color'])
                bids_df = pd.DataFrame(columns=['price', 'symbol', 'id', 'side', 'size','color'])
                bestasks_df = pd.DataFrame(columns=['price', 'symbol', 'id', 'side', 'size', 'color', "timestamp"])
                bestbids_df = pd.DataFrame(columns=['price', 'symbol', 'id', 'side', 'size', 'color', "timestamp"])

                book_data = line_obj["book"]
                time_str = line_obj["timestamp"]
                book_time = microseconds_to_datetime(int(time_str)/1000)
                timestamp = book_time
                # display_lob =[]
                asks_data = book_data["asks"]
                bids_data = book_data["bids"]
                for ask in asks_data:
                    order = {}
                    order["price"] = ask[0] / 1000
                    order["symbol"] = line_obj["symbol"]
                    order["id"]= line_obj["sequence"]
                    order["side"] = "Ask"
                    order["size"] = ask[1]
                    order["color"] = ask_color
                    asks[order["price"]] = order
                for bid in bids_data:
                    order = {}
                    order["price"] = bid[0] / 1000
                    order["symbol"] = line_obj["symbol"]
                    order["id"] = line_obj["sequence"]
                    order["side"] = "Bid"
                    order["size"] = bid[1]
                    order["color"] = bid_color
                    bids[order["price"]] = order

            elif line_obj["type"] == "incremental":
                '''
                {
                    "book": {
                        "asks": [
                            [
                                593290000,
                                8636
                            ]
                        ],
                        "bids": []
                    },
                    "depth": 30,
                    "sequence": 6555127997,
                    "symbol": "BTCUSD",
                    "timestamp": 1617455135687631400,
                    "type": "incremental"
                }
                '''
                book_data = line_obj["book"]
                time_str = line_obj["timestamp"]
                book_time = microseconds_to_datetime(int(time_str) / 1000)
                timestamp = book_time
                # display_lob =[]
                asks_data = book_data["asks"]
                bids_data = book_data["bids"]
                for ask in asks_data:
                    order = {}
                    order["price"] = ask[0] / 1000
                    order["size"] = ask[1]
                    order["symbol"] = line_obj["symbol"]
                    order["id"] = line_obj["sequence"]
                    order["side"] = "Ask"
                    order["color"] = ask_color
                    if order["size"]==0:
                        if order["price"] in  asks:
                            del asks[order["price"]]
                        else:
                            print("important noise info")
                    else:
                        asks[order["price"]] = order
                for bid in bids_data:
                    order = {}
                    order["price"] = bid[0] / 1000
                    order["size"] = bid[1]
                    order["symbol"] = line_obj["symbol"]
                    order["id"] = line_obj["sequence"]
                    order["side"] = "Bid"
                    order["color"] = bid_color
                    if order["size"]==0:
                        if order["price"] in bids:
                            del bids[order["price"]]
                        else:
                            print("important noise info")
                    else:
                        bids[order["price"]] = order
                # display_lob =[]


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

            bids_df = pd.DataFrame(display_bids, columns=['price', 'symbol', 'id', 'side', 'size', 'color'])

            if len(asks) < display_count:
                start = len(asks)
            else:
                start = display_count

            sorted_asks = sorted(asks)
            display_asks = []
            for i in range(0, start):
                display_asks.append(asks[sorted_asks[i]])

            asks_df = pd.DataFrame(display_asks, columns=['price', 'symbol', 'id', 'side', 'size', 'color'])

            best_ask = copy.deepcopy(asks[sorted_asks[0]])
            # print(best_ask)
            best_ask["timestamp"]=timestamp
            best_bid = copy.deepcopy(bids[sorted_bids[-1]])
            best_bid["timestamp"]=timestamp
            bestasks_df = bestasks_df.append(
                pd.DataFrame([best_ask], columns=['price', 'symbol', 'id', 'side', 'size', 'color', "timestamp"]))
            bestbids_df = bestbids_df.append(
                pd.DataFrame([best_bid], columns=['price', 'symbol', 'id', 'side', 'size', 'color', "timestamp"]))
            # print(best_bid)
            #print("step_count check")
            if step_count <= 1:
                break
            else:
                step_count = step_count - 1

        elif "sequence" in line_obj and line_obj["type"] == "incremental":
            '''
            {
                "sequence": 6555128548,
                "symbol": "BTCUSD",
                "trades": [
                    [
                        1617455137632952800,
                        "Buy",
                        593065000,
                        10725
                    ]
                ],
                "type": "incremental"
            }
            '''
            trades_data = line_obj["trades"]
            for trade_obj in trades_data:
                trade={}
                trade["symbol"]=line_obj["symbol"]
                trade['tick_direction'] = "NoMeaning"
                trade["price"]=trade_obj[2]/1000
                trade["size"] = trade_obj[3]
                trade["timestamp"]=microseconds_to_datetime(trade_obj[0]/1000)
                trade["trade_time_ms"] = trade_obj[0]
                trade["side"] = trade_obj[1]
                trade["trade_id"] = line_obj["sequence"]

                timestamp = trade["timestamp"]
                if trade["side"]=="Buy":
                    trade["color"]=buy_color
                    buys_df=buys_df.append(pd.DataFrame([trade],columns=['symbol', 'tick_direction', 'price', 'size',
                                                                         'timestamp', "trade_time_ms", "side","trade_id","color"]))
                    #buys.append(data)
                elif trade["side"]=="Sell":
                    trade["color"] = sell_color
                    sells_df=sells_df.append(pd.DataFrame([trade],columns=['symbol', 'tick_direction', 'price', 'size',
                                                                         'timestamp', "trade_time_ms", "side","trade_id","color"]))
                #sells.append(data)
                # print(trade)
                trades_df=trades_df.append(pd.DataFrame([trade],columns=['side', 'trade_id', 'price', 'size', 'symbol', "timestamp", "color"]))

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