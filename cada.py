'''
Cross-market Arbitrage Data Analysis
'''
import os
import signal
import sys
from decimal import Decimal
import json

def hande_quote(quote,quotes):
    price = Decimal(quote[0])
    volume = Decimal(quote[1])
    quotes[price] = volume
    if volume == Decimal(0) and price in quotes:
        del quotes[price]

def cada():
    binan_bids={}
    binan_asks={}
    huobi_bids = {}
    huobi_asks = {}
    okex_bids={}
    okex_asks={}
    i=0
    with open("./data/ConvergeSubscriber2021-03-01") as f:
        for line in f:
            line_obj = json.loads(line)
            #print(line_obj)
            if "stream" in line_obj and line_obj["stream"]=="btcusdt@depth@100ms":#Binance
                bids = line_obj["data"]["b"]
                asks = line_obj["data"]["a"]
                for bid in bids:
                    hande_quote(bid,binan_bids)
                for ask in asks:
                    hande_quote(ask,binan_asks)
            elif "id" in line_obj and line_obj["id"]=="id4"and line_obj["rep"]=="market.btcusdt.mbp.150":#Huobi First Req

                bids = line_obj["data"]["bids"]
                asks = line_obj["data"]["asks"]
                for bid in bids:
                    hande_quote(bid,huobi_bids)
                #print("huobi_asks#1--------------------{}".format(asks))
                for ask in asks:
                    hande_quote(ask,huobi_asks)
            elif "ch" in line_obj and line_obj["ch"]=="market.btcusdt.mbp.150":#Huobi update
                bids = line_obj["tick"]["bids"]
                asks = line_obj["tick"]["asks"]
                for bid in bids:
                    hande_quote(bid, huobi_bids)
                #print("huobi_asks##--------------------{}".format(asks))
                for ask in asks:

                    hande_quote(ask, huobi_asks)
            elif "table" in line_obj and line_obj["table"]=="spot/depth_l2_tbt":#Okex
                bids = line_obj["data"][0]["bids"]
                asks = line_obj["data"][0]["asks"]
                for bid in bids:
                    hande_quote(bid, okex_bids)#ask:["48173.6","0.01052713","0","1"]
                for ask in asks:
                    hande_quote(ask, okex_asks)
            else:#Bitfinex is omited
                continue

            bids_price=set()
            #print(binan_bids)
            bids_price=bids_price.union(set(binan_bids.keys()))
            bids_price=bids_price.union(set(huobi_bids.keys()))
            bids_price=bids_price.union(set(okex_bids.keys()))
            sorted_bids = list(bids_price)

            sorted_bids.sort()

            asks_price = set()
            #print("---------------1111")
            #print(binan_asks)
            #print("---------------1112")
            #print(huobi_asks)
            #print("---------------1113")
            #print(okex_asks)
            asks_price=asks_price.union(set(binan_asks.keys()))
            asks_price=asks_price.union(set(huobi_asks.keys()))
            asks_price=asks_price.union(set(okex_asks.keys()))
            sorted_asks = list(asks_price)
            sorted_asks.sort()

            best_bid= sorted_bids[-1]
            best_ask = sorted_asks[0]
            #print(len(asks_price))
            if best_bid>best_ask:
                i=i+1
                if i>=1500:
                    sys.exit(0)
                if (best_bid-best_ask)/best_bid>0.0005:
                    print("###########################{}:best_bid:{},best_ask:{},spread::{}".format(i,best_bid,best_ask,(best_bid-best_ask)/best_bid))
                #sys.exit(0)

def exit(signum, frame):
    print('You choose to stop me!')
    sys.exit(0)
if __name__ == '__main__':
    print("begin!")
    signal.signal(signal.SIGTERM, exit)
    cada()