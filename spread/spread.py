#!/usr/bin/env python3
import json
import sys
import time
import ccxt
import smtplib
import os

config = json.load(open('config.json'))
Base = config["Base"]
Quote = config["Quote"]
Contract = config["Contract"]
Spread_threshold = config["Spread_threshold"]
Close_threshold = config["Close_threshold"]
Min_MarginRatio = config["Min_MarginRatio"]
Min_trade_amount = config["Min_trade_amount"]
biggest_amount = 0.2
side = 0

long_amount_A = 0
short_amount_A = 1

open_long = 1
open_short = 2
close_long = 3
close_short = 4
hit = 0

A = ccxt.binance(config["binance"])
B = ccxt.okex3(config["okex"])
A.load_markets()
B.load_markets()

A_pair = ""
B_pair = Base + '-' + Quote


for symbol in A.markets:
    if Base in symbol:
        A_pair = symbol
        break

for symbol in B.markets:
    if B_pair in symbol:
        market = B.markets[symbol]
        if market['info']['alias'] == Contract:
            B_pair = market['symbol']
            break

count = 0

while True:
    try:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
              "hit:", hit)
        if count % 5 == 0:
            time.sleep(5)
            # marginRatio A
            balance_A = A.fetchBalance()
            marginRatio_A = float(balance_A["info"]["totalMarginBalance"]) / \
                            (10 * float(balance_A["info"]["totalInitialMargin"])) if \
                            float(balance_A["info"]["totalInitialMargin"]) != 0 else 1
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  A.id.ljust(7), "marginRatio(big safe):", "%3.4f" %marginRatio_A)
            # trade avaliable Amount BTC
            order_book_A = A.fetch_order_book(A_pair)
            bid0_price_A = order_book_A['bids'][0][0]
            trade_availableAmount_A = (float(balance_A["info"]["totalMarginBalance"]) / 10 \
                                      / Min_MarginRatio - \
                                      float(balance_A["info"]["totalInitialMargin"])) / \
                                      bid0_price_A
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  A.id.ljust(7), "available trade BTC amount:", "%3.4f" %trade_availableAmount_A)
            sell_availAmount_A = trade_availableAmount_A * 10 + 2 * long_amount_A
            buy_availAmount_A = trade_availableAmount_A * 10 + 2 * short_amount_A
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  A.id.ljust(7),
                  "sell available BTC amount:", "%3.4f" %sell_availAmount_A,
                  "buy available BTC amount:", "%3.4f" %buy_availAmount_A)

            # marginRatio B
            balance_B = B.fetchBalance()
            marginRatio_B = float(balance_B["info"]["info"]['btc']['margin_ratio'])
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  B.id.ljust(7), "marginRatio(big safe):", "%3.4f" %marginRatio_B)

            # trade available Amount BTC
            trade_availableAmount_B = (float(balance_B["info"]["info"]['btc']['equity']) / \
                                       Min_MarginRatio / 10 \
                                       - float(balance_B["info"]["info"]['btc']['margin_frozen']))
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  B.id.ljust(7), "available trade BTC amount:", "%3.4f" %trade_availableAmount_B)
            position_B = B.futures_get_instrument_id_position({"instrument_id": B_pair})
            hold_long_avail_qty_B = float(position_B["holding"][0]["long_avail_qty"])
            hold_short_avail_qty_B = float(position_B["holding"][0]["short_avail_qty"])
            order_book_B = B.fetch_order_book(B_pair)
            bid0_price_B = order_book_B['bids'][0][0]
            sell_availAmount_B = trade_availableAmount_B * 10 + \
                                 2 * hold_long_avail_qty_B * 100 / bid0_price_B
            buy_availAmount_B = trade_availableAmount_B * 10 + \
                                2 * hold_short_avail_qty_B * 100 / bid0_price_B
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  B.id.ljust(7),
                  "sell available BTC amount:", "%3.4f" %sell_availAmount_B,
                  "buy available BTC amount:", "%3.4f" %buy_availAmount_B)

            time.sleep(1)
            AopenOrders = A.fetchOpenOrders(symbol=A_pair)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  A.id.ljust(7), "order:", AopenOrders)
            BopenOrders = B.fetchOpenOrders(symbol=B_pair)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  B.id.ljust(7), "order:", BopenOrders)

        count += 1
        time.sleep(30)
        order_book_A = A.fetch_order_book(A_pair)
        bid0_price_A = order_book_A['bids'][0][0]
        bid0_amount_A = order_book_A['bids'][0][1]
        ask0_price_A = order_book_A['asks'][0][0]
        ask0_amount_A = order_book_A['asks'][0][1]
        bidask_spread_A = ask0_price_A - bid0_price_A
        timestamp_A = time.time()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), A.id.ljust(7),
                "bids:",
                "%5.2f" %bid0_price_A, "%5.2f" %bid0_amount_A,
                "asks:",
                "%5.2f" %ask0_price_A, "%5.2f" %ask0_amount_A,
                "bss:",
                "%5.2f" %bidask_spread_A)

        order_book_B = B.fetch_order_book(B_pair)
        bid0_price_B = order_book_B['bids'][0][0]
        bid0_amount_B = order_book_B['bids'][0][1] * 100 / bid0_price_B
        ask0_price_B = order_book_B['asks'][0][0]
        ask0_amount_B = order_book_B['asks'][0][1] * 100 / ask0_price_B
        bidask_spread_B = ask0_price_B - bid0_price_B
        timestamp_B = time.time()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), B.id.ljust(7),
                "bids:",
                "%5.2f" %bid0_price_B, "%5.2f" %bid0_amount_B,
                "asks:",
                "%5.2f" %ask0_price_B, "%5.2f" %ask0_amount_B,
                "bss:",
                "%5.2f" %bidask_spread_B)
        if timestamp_B - timestamp_A > 0.1:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  "time delay to big", timestamp_B - timestamp_A)
            continue

        AaskBbid_spread = (ask0_price_A - bid0_price_B)/bid0_price_B
        BaskAbid_spread = (ask0_price_B - bid0_price_A)/bid0_price_A
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
              B.id.ljust(7), "->", A.id.ljust(7), "profit: %+.4f" %AaskBbid_spread)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
              A.id.ljust(7), "->", B.id.ljust(7), "profit: %+.4f" %BaskAbid_spread)

        if BaskAbid_spread < Close_threshold:
            hit += 1
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), A.id.ljust(7),
                  "sell", B.id.ljust(7), "buy", "spread:", AaskBbid_spread, "hit:", hit)
            continue
            AaskBbid_amount = min(bid0_amount_A, ask0_amount_B, biggest_amount,
                                  sell_availAmount_A, buy_availAmount_B)
            B_amount = int(AaskBbid_amount * bid0_price_B / 100)
            AaskBbid_amount = B_amount * 100 / bid0_price_B
            if AaskBbid_amount < Min_trade_amount:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                      "Too small trade amount")
            Aask = A.createLimitSellOrder(A_pair, AaskBbid_amount, bid0_price_A)

            position_B = B.futures_get_instrument_id_position({"instrument_id": B_pair})
            hold_short_avail_qty_B = float(position_B["holding"][0]["short_avail_qty"])
            if hold_short_avail_qty_B > B_amount:
                Bbid = B.create_order(B_pair, close_short, "limit", "buy",
                                      B_amount,
                                      ask0_price_B)
            else:
                Bbid = B.create_order(B_pair, close_short, "limit", "buy",
                                      hold_short_avail_qty_B,
                                      ask0_price_B)
                Bbid = B.create_order(B_pair, open_long, "limit", "buy",
                                      B_amount - hold_short_avail_qty_B,
                                      ask0_price_B)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), A.id.ljust(7),
                  "sell", B.id.ljust(7), "buy")

        if BaskAbid_spread > Spread_threshold:
            hit += 1
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), B.id.ljust(7),
                  "sell", A.id.ljust(7), "buy", "spread:", BaskAbid_spread, "hit:", hit)
            continue
            BaskAbid_amount = min(ask0_amount_A, bid0_amount_B, biggest_amount,
                                  sell_availAmount_B, buy_availAmount_A)
            B_amount = int(BaskAbid_amount * ask0_price_B / 100)
            BaskAbid_amount = B_amount * 100 / ask0_price_B
            if BaskAbid_amount < Min_trade_amount:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                      "Too small trade amount")
            Abid = A.createLimitBuyOrder(A_pair, BaskAbid_amount, ask0_price_A)

            position_B = B.futures_get_instrument_id_position({"instrument_id": B_pair})
            hold_long_avail_qty_B = float(position_B["holding"][0]["long_avail_qty"])
            if hold_long_avail_qty_B > B_amount:
                Bask = B.create_order(B_pair, close_long, "limit", "sell",
                                      B_amount,
                                      bid0_price_B)
            else:
                Bask = B.create_order(B_pair, close_long, "limit", "sell",
                                      hold_long_avail_qty_B,
                                      bid0_price_B)
                Bask = B.create_order(B_pair, open_short, "limit", "sell",
                                      B_amount - hold_long_avail_qty_B,
                                      bid0_price_B)

    except Exception as err:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), err)
