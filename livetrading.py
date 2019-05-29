#!/usr/bin/env python3
"""
Alarm cryptocurrency on binance 4h on Donchian Channel break
By fabius8
"""
from catalyst import run_algorithm
from catalyst.exchange.utils.stats_utils import get_pretty_stats
from catalyst.api import record, symbol, order_target_percent
from catalyst.exchange.utils.stats_utils import extract_transactions
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from logbook import Logger

sender = 'fabius8@aliyun.com'
receivers = ['fabius8@163.com', 'fabius888@126.com']

import matplotlib.pyplot as plt
import pandas as pd
import json
import time

algo_namespace = 'livetrading'
log = Logger(algo_namespace)

auth = json.load(open("auth.json"))

EntryChannelPeriods = 20
ExitChannelPeriods = 20


def initialize(context):
    context.i = -1

    context.stock = symbol('btc_usdt')
    context.base_price = None
    context.freq = '4h'

def send_email(stock, indicator, freq, price, highest, lowest, N,
               positionSizePercent, positionSize,
               context):
    print("send_email")
    text = str(stock)
    text += '\nDonchian Channel break ' + freq
    text += '\nYou must hold position ' + indicator
    text += '\n\nCurrent price: ' + str(price)
    text += '\nUpper: ' + str(highest)
    text += '\nLower: ' + str(lowest)
    text += '\nATR: ' + str(N)
    text += '\nPosition Size Percent: ' + str(positionSizePercent)[0:6] + '%'
    text += '\nPosition Amount: ' + str(positionSize) + ' units'

    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] =  ",".join(receivers)
    try:
        if indicator == "LONG":
            subject = str(stock) + indicator
        elif indicator == "SHORT":
            subject = str(stock) + indicator
        smtpObj = smtplib.SMTP_SSL('smtp.aliyun.com', 465)
        #smtpObj.set_debuglevel(1)
        smtpObj.login(auth['username'], auth['password']);
        message['Subject'] = subject
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        smtpObj.close()
    except smtplib.SMTPException as e:
        print("Send Mail Fail", e)


def ATR(highs, lows, closes):
    high_to_low = highs - lows
    high_to_prev_close = abs(highs[1:] - closes[:-1])
    low_to_prev_close = abs(lows[1:] - closes[:-1])
    TR = high_to_low.combine(high_to_prev_close, max, fill_value=0).combine(low_to_prev_close, max, fill_value=0)
    return TR.sum() / TR.count()


def handle_data(context, data):
    context.i += 1
    # 1 min report
    if context.i % 1 != 0:
        return
    price = data.current(context.stock, 'price')

    closes = data.history(context.stock,
                          'close',
                          bar_count=EntryChannelPeriods + 1,
                          frequency=context.freq)

    highs = data.history(context.stock,
                         'high',
                         bar_count=EntryChannelPeriods + 1,
                         frequency=context.freq)

    lows = data.history(context.stock,
                        'low',
                        bar_count=ExitChannelPeriods + 1,
                        frequency=context.freq)

    N = ATR(highs[1:], lows[1:], closes[1:])

    exchange = context.exchanges['binance']
    for pair in exchange.markets:
        if pair['quote'] == "USDT":
            print(pair['base'].lower() + '_' + pair['quote'].lower())

if __name__ == '__main__':
    run_algorithm(
        capital_base=1000,
        data_frequency='minute',
        initialize=initialize,
        handle_data=handle_data,
        analyze=None,
        exchange_name='binance',
        algo_namespace='livetrading',
        live=True,
        simulate_orders=False,
        quote_currency='usdt'
    )
