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
Trade_mode = config["trade_mode"]

A = ccxt.binance(config["binance"])
old_fundingRate = None


while True:
    try:
        print("="*50)
        log = ""
        fundingRate = A.fapiPublicGetPremiumIndex()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        for i in fundingRate:
            log = i['symbol'].ljust(8) + \
                  " fundingRate:" + \
                  " %.6f" % (float(i['lastFundingRate']) * 100)
            if old_fundingRate is None:
                print(log)
                continue
            for j in old_fundingRate:
                if j['symbol'] == i['symbol']:
                    delta_fundingRate = float(i['lastFundingRate']) - \
                                        float(j['lastFundingRate'])
                    if delta_fundingRate == 0:
                        break
                    log += ' %+.6f' % (delta_fundingRate * 100)
                    break
            print(log)
        old_fundingRate = fundingRate
    except Exception as err:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), err)
        time.sleep(60)
        continue
    time.sleep(60)


