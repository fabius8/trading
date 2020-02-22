#!/usr/bin/env python3
import json
import time
import ccxt

config = json.load(open('config.json'))

A = ccxt.binance(config["binance"])
A_spot = ccxt.binance(config["binance_spot"])
B = ccxt.okex3(config["okex"])

A.load_markets()
A_spot.load_markets()
B.load_markets()


def get_binance_balance(A, A_spot):
    try:
        balance_A = A.fetchBalance()
        print(balance_A["info"]["totalMarginBalance"])
        balance_spot_A = A_spot.fetchBalance()
        print(balance_spot_A)
    except Exception as err:
        print(err)
        pass


def get_okex_balance(B):
    try:
        balance_swap_B = B.fetchBalance(params={"type": "swap"})
        balance_futures_B = B.fetchBalance(params={"type": "futures"})
        total_btc = float(balance_swap_B["info"]["info"][0]['equity']) + \
                    float(balance_futures_B["info"]["info"]['btc']['equity'])
        print(total_btc)
    except Exception as err:
        print(err)
        pass


while True:
    get_binance_balance(A, A_spot)
    get_okex_balance(B)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    time.sleep(100)
