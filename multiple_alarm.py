#!/usr/bin/env python3
"""
Alarm cryptocurrency on binance 4h on Donchian Channel break
By fabius8
"""
from catalyst import run_algorithm
import numpy as np
from catalyst.api import record, symbol, order_target_percent
from catalyst.exchange.utils.stats_utils import extract_transactions
import smtplib
from email.mime.text import MIMEText
from email.header import Header
sender = 'fabius8@aliyun.com'
receivers = ['fabius888@163.com']

import matplotlib.pyplot as plt
import pandas as pd
import json
import time

auth = json.load(open("auth.json"))

EntryChannelPeriods = 20
ExitChannelPeriods = 20


def initialize(context):
    context.i = -1
    context.stocks = []
    exchange = context.exchanges['binance']
    for pair in exchange.markets:
        if pair['quote'] == "USDT":
            context.stocks.append(symbol((pair['base'].lower() + '_' + pair['quote'].lower())))
    context.base_price = None
    context.freq = '4h'
    context.report = {}
    context.report_interval = {}
    for stock in context.stocks:
        context.report[stock] = 0
        context.report_interval[stock] = 240


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

    context.report[stock] = indicator
    context.report_interval[stock] = 240

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

    for stock in context.stocks:
        if context.report_interval[stock] > 0:
            context.report_interval[stock] -= 1
            continue
        try:
            price = data.current(stock, 'price')
            closes = data.history(stock,
                                  'close',
                                  bar_count=EntryChannelPeriods + 1,
                                  frequency=context.freq)

            highs = data.history(stock,
                                 'high',
                                 bar_count=EntryChannelPeriods + 1,
                                 frequency=context.freq)

            lows = data.history(stock,
                                'low',
                                bar_count=ExitChannelPeriods + 1,
                                frequency=context.freq)
        except Exception as e:
            print(e)
            continue

        N = ATR(highs[1:], lows[1:], closes[1:])
        print(stock, "ATR:", N)

        highs = highs[-21:-1]
        lows = lows[-21:-1]

        highest = highs.max()
        lowest = lows.min()
        print(stock, price, highest, lowest)

        positionSizePercent = price / N
        positionSize = 23000 * 0.01 / N
        if price > highest and context.report[stock] != "LONG":
            indicator = "LONG"
            send_email(stock, indicator, context.freq,
                       price, highest, lowest, N,
                       positionSizePercent, positionSize,
                       context)
        elif price < lowest and context.report[stock] != "SHORT":
            indicator = "SHORT"
            send_email(stock, indicator, context.freq,
                       price, highest, lowest, N,
                       positionSizePercent, positionSize,
                       context)


if __name__ == '__main__':
    run_algorithm(
        capital_base=23000,
        data_frequency='minute',
        initialize=initialize,
        handle_data=handle_data,
        analyze=None,
        exchange_name='binance',
        algo_namespace='Donchian Channel',
        live=True,
        quote_currency='usdt'
    )
