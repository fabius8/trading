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
        if market['info']['alias'] == 'quarter':
            B_pair = market['symbol']
            break

A.load_markets()
B.load_markets()

while True:
    try:
        time.sleep(1)
        order_book_A = A.fetch_order_book(A_pair)
        bid0_price_A = order_book_A['bids'][0][0]
        bid0_amount_A = order_book_A['bids'][0][1]
        ask0_price_A = order_book_A['asks'][0][0]
        ask0_amount_A = order_book_A['asks'][0][1]
        bidask_spread_A = ask0_price_A - bid0_price_A
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "binance:",
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
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "okex:   ",
                "bids:",
                "%5.2f" %bid0_price_B, "%5.2f" %bid0_amount_B,
                "asks:",
                "%5.2f" %ask0_price_B, "%5.2f" %ask0_amount_B,
                "bss:",
                "%5.2f" %bidask_spread_B)
        AaskBbid_spread = (ask0_price_A - bid0_price_B)/bid0_price_B
        BaskAbid_spread = (ask0_price_B - bid0_price_A)/bid0_price_A
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "Buy okex -> Sell binance:", "%.4f" %AaskBbid_spread)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                "Buy binance -> Sell okex:", "%.4f" %BaskAbid_spread)
        balance_B = B.fetchBalance()
        print(balance)
    except Exception as err:
        print(err)
