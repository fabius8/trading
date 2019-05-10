"""
Test BTC on binance 4h on Donchian Channel
By fabius8
"""
from catalyst import run_algorithm
import numpy as np
from catalyst.api import record, symbol, order_target_percent
from catalyst.exchange.utils.stats_utils import extract_transactions
import smtplib
from email.mime.text import MIMEText
from email.header import Header
sender = 'fabius888@126.com'
receivers = ['fabius8@163.com', 'fabius888@126.com']

import matplotlib.pyplot as plt
import pandas as pd
import json

auth = json.load(open("auth.json"))

EntryChannelPeriods = 20
ExitChannelPeriods = 20


def initialize(context):
    context.i = -1
    context.stocks = [
            symbol('btc_usdt'),
            symbol('eth_usdt'),
            symbol('bnb_usdt'),
            symbol('ltc_usdt'),
            symbol('eos_usdt'),
            symbol('bchabc_usdt')]
    context.base_price = None
    context.freq = '4h'

def send_email(stock, indicator, freq, price, highest, lowest, N):
    print("send_email")
    text = str(stock)
    text += '\nDonchian Channel break ' + freq
    text += '\nYou must hold position ' + indicator
    text += '\n\nCurrent price: ' + str(price)
    text += '\nUpper: ' + str(highest)
    text += '\nLower: ' + str(lowest)
    text += '\nATR: ' + str(N)
    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] =  ",".join(receivers)
    try:
        if indicator == "LONG":
            subject = str(stock) + indicator
        elif indicator == "SHORT":
            subject = str(stock) + indicator
        smtpObj = smtplib.SMTP_SSL('smtp.126.com', 465)
        smtpObj.set_debuglevel(1)
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
    # 2 hour report
    if context.i % 120 != 0:
        return

    for stock in context.stocks:
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

        N = ATR(highs[1:], lows[1:], closes[1:])
        print(stock, "ATR:", N)

        highs = highs[-21:-1]
        lows = lows[-21:-1]

        highest = highs.max()
        lowest = lows.min()
        print(stock, price, highest, lowest)

        if price > highest:
            indicator = "LONG"
            send_email(stock, indicator, context.freq, price, highest, lowest, N)
        elif price < lowest:
            indicator = "SHORT"
            send_email(stock, indicator, context.freq, price, highest, lowest, N)


if __name__ == '__main__':
    run_algorithm(
        capital_base=1000,
        data_frequency='minute',
        initialize=initialize,
        handle_data=handle_data,
        analyze=None,
        exchange_name='binance',
        algo_namespace='Donchian Channel',
        live=True,
        quote_currency='usdt'
    )
