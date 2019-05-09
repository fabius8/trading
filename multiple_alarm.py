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
receivers = ['fabius8@163.com', '18994900535@163.com']

import matplotlib.pyplot as plt
import pandas as pd

EntryChannelPeriods = 20
ExitChannelPeriods = 20


def initialize(context):
    context.i = -1
    context.stocks = [symbol('btc_usdt'), symbol('eth_usdt'), symbol('bnb_usdt')]
    context.base_price = None

def send_email(stock, indicator):
    try:
        if indicator == "LONG":
            subject = stock + indictor
        elif indicator == "SHORT":
            subject = stock + indictor
        smtpObj = smtplib.SMTP('smtp.126.com', 25)
        smtpObj.login('','');
        smtpObj.sendmail(sender, receivers, message.as_string())
        message['Subject'] = Header(subject, 'utf-8')
        smtpObj.sendmail(sender, receivers, message.as_string())
    except smtplib.SMTPException:
        pass


def handle_data(context, data):
    context.i += 1
    if context.i % 5 != 0:
        return

    for stock in context.stocks:
        price = data.current(stock, 'price')

        highest = data.history(stock,
                'high',
                bar_count=EntryChannelPeriods + 1,
                frequency="4h")[-21:-1].max()
        lowest = data.history(stock,
                'low',
                bar_count=ExitChannelPeriods + 1,
                frequency="4h")[-21:-1].min()

        print(stock, price, highest, lowest)

        if price > highest:
            indicator = "LONG"
            send_email(stock, indicator)
        elif price < lowest:
            indicator = "SHORT"
            send_email(stock, indicator)


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
