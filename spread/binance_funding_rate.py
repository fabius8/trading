#!/usr/bin/env python3
import json
import sys
import time
import ccxt
import smtplib
import os

config = json.load(open('config_funding.json'))

binance_future = ccxt.binance(config["binance_future"])
binance_spot = ccxt.binance(config["binance_spot"])
binance_future.load_markets()
binance_spot.load_markets()

old_fundingRate = None

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_spread_close(symbol, future, spot):
    try:
        symbol = symbol.replace('USDT', '/USDT')
        order_book_A = future.fetch_order_book(symbol)
        bid0_A = order_book_A['bids'][0][0]
        ask0_A = order_book_A['asks'][0][0]
        order_book_B = spot.fetch_order_book(symbol)
        bid0_B = order_book_B['bids'][0][0]
        ask0_B = order_book_B['asks'][0][0]
        log = " %+.2f" % ((bid0_A - ask0_B)/ask0_B*100) + "%" + \
              " %+.2f" % ((bid0_B - ask0_A)/ask0_A*100) + "%"
    except Exception as err:
        log = " HAHA ERROR!"
    return log


while True:
    try:
        print("="*30)
        log = ""
        fundingRate = binance_future.fapiPublicGetPremiumIndex()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print(" "*10, "fundRate", "minRate", "sell  buy")
        for i in fundingRate:
            spread = get_spread_close(i['symbol'], binance_future, binance_spot)
            log = i['symbol'].ljust(10) + \
                  " %+.3f" % (float(i['lastFundingRate']) * 100)
            if old_fundingRate is None:
                log += " " + "-"*4
                log += spread
                if 'BTC' in log:
                    log = bcolors.OKGREEN + log + bcolors.ENDC
                print(log)
                continue
            for j in old_fundingRate:
                if j['symbol'] == i['symbol']:
                    delta_fundingRate = float(i['lastFundingRate']) - \
                                        float(j['lastFundingRate'])
                    if delta_fundingRate == 0:
                        log += " "*7
                        log += spread
                        break
                    log += ' %+.3f' % (delta_fundingRate * 100)
                    log += spread
                    break
            if 'BTC' in log:
                log = bcolors.OKGREEN + log + bcolors.ENDC
            print(log)
            time.sleep(1)
        old_fundingRate = fundingRate
    except Exception as err:
        old_fundingRate = fundingRate
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), err)
        binance_future.load_markets()
        binance_spot.load_markets()
        time.sleep(60)
        continue
    time.sleep(60)


