from decimal import Decimal
import json
with open('data/OkexSubscriber2020-05-24', 'r') as f:
    #update_count =0
    bid_mean=0
    bid_count=0
    bid_var=0
    ask_mean=0
    ask_count=0
    ask_var=0
    ask_dist={}
    bid_dist={}
    best_bid_size_mean=0
    best_ask_size_mean=0
    spread_mean=0
    ticket_count=0
    for line in f.readlines():
        line_data = json.loads(line)

        if "table" in line_data and line_data["table"]=="spot/trade":
            print(line_data);
            trade_data=line_data["data"]
            for trade in trade_data:
                trade_size = Decimal(trade["size"])
                if trade["side"]=="sell":

                    ask_mean = (ask_mean*ask_count+trade_size)/(ask_count + 1)
                    ask_var = (ask_var * ask_count+(trade_size-Decimal(0.150569))**2)/(ask_count + 1)
                    ask_count = ask_count + 1
                    if trade_size < 0.001:
                        ask_dist["0.001"] = (0 if "0.001" not in ask_dist else ask_dist["0.001"]) + 1
                    elif trade_size < 0.005:
                        ask_dist["0.005"] = (0 if "0.005" not in ask_dist else ask_dist["0.005"]) + 1
                    elif trade_size<0.01:
                        ask_dist["0.01"]= (0 if "0.01" not in ask_dist else ask_dist["0.01"])+1
                    elif trade_size<0.02:
                        ask_dist["0.02"] = (0 if "0.02" not in ask_dist else ask_dist["0.02"]) + 1
                    elif trade_size<0.05:
                        ask_dist["0.05"] = (0 if "0.05" not in ask_dist else ask_dist["0.05"]) + 1
                    elif trade_size<0.1:
                        ask_dist["0.1"] = (0 if "0.1" not in ask_dist else ask_dist["0.1"]) + 1
                    elif trade_size<0.15:
                        ask_dist["0.15"] = (0 if "0.15" not in ask_dist else ask_dist["0.15"]) + 1
                    elif trade_size<0.2:
                        ask_dist["0.2"] = (0 if "0.2" not in ask_dist else ask_dist["0.2"]) + 1
                    elif trade_size<0.5:
                        ask_dist["0.5"] = (0 if "0.5" not in ask_dist else ask_dist["0.5"]) + 1
                    elif trade_size<1:
                        ask_dist["1"] = (0 if "1" not in ask_dist else ask_dist["1"]) + 1
                    else:
                        ask_dist["1.0"] = (0 if "1.0" not in ask_dist else ask_dist["1.0"]) + 1


                elif trade["side"]=="buy":
                    bid_mean=(bid_mean*bid_count+trade_size)/(bid_count+1)
                    bid_var = (bid_var * bid_count + (trade_size - Decimal(0.147236)) ** 2 )/ (bid_count + 1)
                    bid_count=bid_count+1
                    if trade_size < 0.001:
                        bid_dist["0.001"] = (0 if "0.001" not in bid_dist else bid_dist["0.001"]) + 1
                    elif trade_size < 0.005:
                        bid_dist["0.005"] = (0 if "0.005" not in bid_dist else bid_dist["0.005"]) + 1
                    elif trade_size<0.01:
                        bid_dist["0.01"]= (0 if "0.01" not in bid_dist else bid_dist["0.01"])+1
                    elif trade_size<0.02:
                        bid_dist["0.02"] = (0 if "0.02" not in bid_dist else bid_dist["0.02"]) + 1
                    elif trade_size<0.05:
                        bid_dist["0.05"] = (0 if "0.05" not in bid_dist else bid_dist["0.05"]) + 1
                    elif trade_size<0.1:
                        bid_dist["0.1"] = (0 if "0.1" not in bid_dist else bid_dist["0.1"]) + 1
                    elif trade_size<0.15:
                        bid_dist["0.15"] = (0 if "0.15" not in bid_dist else bid_dist["0.15"]) + 1
                    elif trade_size<0.2:
                        bid_dist["0.2"] = (0 if "0.2" not in bid_dist else bid_dist["0.2"]) + 1
                    elif trade_size<0.5:
                        bid_dist["0.5"] = (0 if "0.5" not in bid_dist else bid_dist["0.5"]) + 1
                    elif trade_size<1:
                        bid_dist["1"] = (0 if "1" not in bid_dist else bid_dist["1"]) + 1
                    else:
                        bid_dist["1.0"] = (0 if "1.0" not in bid_dist else bid_dist["1.0"]) + 1

        elif "table" in line_data and line_data["table"] == "spot/ticker":
            line_data = line_data["data"][0]
            best_ask = Decimal(line_data["best_ask"])
            best_bid = Decimal(line_data["best_bid"])
            spread_mean=(spread_mean*ticket_count+(best_ask-best_bid))/(ticket_count+1)

            best_ask_size = Decimal(line_data["best_ask_size"])
            best_ask_size_mean=(best_ask_size_mean*ticket_count+best_ask_size)/(ticket_count+1)

            best_bid_size = Decimal(line_data["best_bid_size"])
            best_bid_size_mean = (best_bid_size_mean * ticket_count + best_bid_size) / (ticket_count + 1)

            ticket_count=ticket_count+1

    print("ask_count:%u"%ask_count)
    print("ask_mean:%f" % ask_mean)
    print("ask_var:%f" % ask_var)
    print(ask_dist)
    print("bid_count:%u" % bid_count)
    print("bid_mean:%f" % bid_mean)
    print("bid_var:%f" % bid_var)
    print(bid_dist)
    print("spread_mean%f"%spread_mean)
    print("best_ask_size_mean%f" % best_ask_size_mean)
    print("best_bid_size_mean%f" % best_bid_size_mean)



