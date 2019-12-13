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
biggest_amount = 0.2
side = 0


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
        if count % 100 == 0:
            time.sleep(5)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  "get balance")
            balance_A = A.fetchBalance()
            marginRatio_A = float(balance_A["info"]["totalMaintMargin"])/ \
                            float(balance_A["info"]["totalMarginBalance"])
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  A.id.ljust(7), "marginRatio:", "%3.4f" %marginRatio_A)

            balance_B = B.fetchBalance()
            marginRatio_B = 1 / (1 + float(balance_B["info"]["info"]['btc']['margin_ratio'])) / 100
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  B.id.ljust(7), "marginRatio:", "%3.4f" %marginRatio_B)
            time.sleep(1)
            AopenOrders = A.fetchOpenOrders(symbol=A_pair)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  A.id.ljust(7), AopenOrders)
            BopenOrders = B.fetchOpenOrders(symbol=B_pair)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  B.id.ljust(7), BopenOrders)

        count += 1
        time.sleep(30)
        order_book_A = A.fetch_order_book(A_pair)
        bid0_price_A = order_book_A['bids'][0][0]
        bid0_amount_A = order_book_A['bids'][0][1]
        ask0_price_A = order_book_A['asks'][0][0]
        ask0_amount_A = order_book_A['asks'][0][1]
        bidask_spread_A = ask0_price_A - bid0_price_A
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
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), B.id.ljust(7),
                "bids:",
                "%5.2f" %bid0_price_B, "%5.2f" %bid0_amount_B,
                "asks:",
                "%5.2f" %ask0_price_B, "%5.2f" %ask0_amount_B,
                "bss:",
                "%5.2f" %bidask_spread_B)
        AaskBbid_spread = (ask0_price_A - bid0_price_B)/bid0_price_B
        BaskAbid_spread = (ask0_price_B - bid0_price_A)/bid0_price_A
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
              "Buy", B.id.ljust(7), "-> Sell", A.id.ljust(7), "%+.4f" %AaskBbid_spread)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
              "Buy", A.id.ljust(7), "-> Sell", B.id.ljust(7), "%+.4f" %BaskAbid_spread)

        #if AaskBbid_spread > float(Spread_threshold):
        if False:
            AaskBbid_amount = min(bid0_amount_A, ask0_amount_B, biggest_amount)
            #Aask = A.createLimitSellOrder(A_pair, AaskBbid_amount, bid0_price_A)
            #Bbid = B.createLimitBuyOrder(B_pair, AaskBbid_amount, ask0_price_B)
            Bbid = B.create_order(B_pair, "limit", "buy", 1, 6600)
            #print(Aask)
            print(Bbid)

        #if BaskAbid_spread > float(Spread_threshold):


    except Exception as err:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), err)
