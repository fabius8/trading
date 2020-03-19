#!/usr/bin/env python3
import json
import sys
import time
import ccxt
import smtplib
import os

config = json.load(open('config_funding.json'))

okex_future = ccxt.okex3(config["okex_future"])
okex_spot = ccxt.okex3(config["okex_spot"])
okex_future.load_markets()
okex_spot.load_markets()

swapusd = []
swapusdt = []
swap = []

for symbol in okex_future.markets:
    if "USD-SWAP" in symbol:
        swapusd.append(symbol)
    if "USDT-SWAP" in symbol:
        swapusdt.append(symbol)

swap = swapusd + swapusdt

old_fundingRate = {}
fundingRate = None


def get_spread_close(symbol, future, spot):
    if "USDT-SWAP" in symbol:
        spot_symbol = symbol.replace('-USDT-SWAP', '/USDT')
    else:
        spot_symbol = symbol.replace('-USD-SWAP', '/USDT')
    order_book_A = future.fetch_order_book(symbol)
    bid0_A = order_book_A['bids'][0][0]
    ask0_A = order_book_A['asks'][0][0]
    order_book_B = spot.fetch_order_book(spot_symbol)
    bid0_B = order_book_B['bids'][0][0]
    ask0_B = order_book_B['asks'][0][0]
    #print(bid0_A, ask0_A, bid0_B, ask0_B)
    log = " %+.2f" % ((bid0_A - ask0_B)/ask0_B*100) + "%" + \
          " %+.2f" % ((bid0_B - ask0_A)/ask0_A*100) + "%"
    return log


while True:
    try:
        print("="*30)
        log = ""
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print(" "*14, "fundRate", "minRate", "sell  buy")
        for i in swap:
            fundingRate = okex_future.swapGetInstrumentsInstrumentIdFundingTime({'instrument_id': i})
            spread = get_spread_close(i, okex_future, okex_spot)
            log = i.ljust(14) + \
                  " %+.4f" % ((float(fundingRate['estimated_rate'])) * 100)
            #if not old_fundingRate:
            #    log += " " + "-"*9
            #    log += spread
            #    print(log)
            #    continue
            if i in old_fundingRate:
                delta_fundingRate = float(fundingRate['estimated_rate']) - \
                                    float(old_fundingRate[i])
                old_fundingRate[i] = float(fundingRate['estimated_rate'])
            else:
                old_fundingRate[i] = float(fundingRate['estimated_rate'])
                log += " " + "-"*7
                log += spread
                print(log)
                continue
            if delta_fundingRate == 0:
                log += " "*7
                log += spread
            else:
                log += ' %+.3f' % (delta_fundingRate * 100)
                log += spread
            print(log)
            time.sleep(1)

    except Exception as err:
        old_fundingRate = fundingRate
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), err)
        okex_future.load_markets()
        okex_spot.load_markets()
        time.sleep(60)
        continue
    time.sleep(60)


