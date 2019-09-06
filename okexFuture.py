#!/usr/bin/env python3
import json
import sys
import time
import ccxt
import smtplib

from email.mime.text import MIMEText
from email.header import Header
sender = 'fabius8@aliyun.com'
receivers = ['fabius888@163.com']
auth = json.load(open("auth.json"))


def beep():
    print("\a\a\a\a\a")


def send_email(basis, futurePrice, stockPrice):
    print("send_email")
    text = 'Basis: ' + str(basis)
    text = '\nFuture Price: ' + str(futurePrice)
    text = '\nStock Price: ' + str(stockPrice)

    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] = ",".join(receivers)
    try:
        subject = "BTC price changing quickly!"
        smtpObj = smtplib.SMTP_SSL('smtp.aliyun.com', 465)
        # smtpObj.set_debuglevel(1)
        smtpObj.login(auth['username'], auth['password'])
        message['Subject'] = subject
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        smtpObj.close()
    except smtplib.SMTPException as e:
        print("Send Mail Fail", e)


config = json.load(open('config.json'))
Base = config["Base"]
Quote = config["Quote"]
Contract = config["Contract"]
futurePair = Base + '-' + Quote
stockPair = Base + '/' + 'USDT'
delay = 2
basis_unit = 0.005
old_amount = 0

exchange = ccxt.okex3(config["okex"])
exchange.load_markets()
for symbol in exchange.markets:
    if futurePair in symbol and symbol != futurePair + '-' + 'SWAP':
        market = exchange.markets[symbol]
        if market['info']['alias'] == 'quarter':
            futurePair = market['symbol']
            break

while True:
    time.sleep(delay)
    orderBookFuture = exchange.fetch_order_book(futurePair)
    orderBookStock = exchange.fetch_order_book(stockPair)
    basis = (orderBookFuture['bids'][0][0] - orderBookStock['bids'][0][0]) / orderBookStock['bids'][0][0]
    basis = (int(basis * 10000))/10000
    new_amount = (basis * 10000) / basis_unit
    if new_amount != old_amount and old_amount != 0:
        print("BTC price is changing quickly!")
        old_amount = new_amount
    print(basis)





