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


def send_email(basis, basis_threshold, futurePrice, stockPrice,
               fundingRate, estimatedRate,
               estimatedRate_threshold):
    print("send_email\n")
    text = 'Basis: ' + str(basis)
    text += '\nThreshold: ' + str(basis_threshold * 100) + '%'
    text += '\nFuture Price: ' + str(futurePrice)
    text += '\nStock Price: ' + str(stockPrice)
    text += '\nFunding Rate: ' + str(fundingRate)
    text += '\nEstimate Rate: ' + str(estimatedRate)
    text += '\nEstimate Threshold: ' + str(estimatedRate_threshold * 100) + '%'

    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = sender
    message['To'] = ",".join(receivers)
    try:
        subject = "okex future change " + str(basis)
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
delay = 5
# 10% price change
basis_threshold = 0.20
old_basis = 0
estimatedRate_threshold = 0.20
old_estimatedRate = 0

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
    fundingRate = exchange.swapGetInstrumentsInstrumentIdFundingTime({'instrument_id': 'BTC-USD-SWAP'})
    estimatedRate = float(int(float(fundingRate['estimated_rate'])*100000))/100000
    if old_estimatedRate == 0:
        old_estimatedRate = estimatedRate
    orderBookFuture = exchange.fetch_order_book(futurePair)
    orderBookStock = exchange.fetch_order_book(stockPair)
    basis = orderBookFuture['bids'][0][0] - orderBookStock['bids'][0][0]
    basis = int(basis)
    if old_basis == 0:
        old_basis = basis
    if abs(abs(basis) - abs(old_basis))/abs(old_basis) > basis_threshold or abs(abs(estimatedRate) - abs(old_estimatedRate)) / abs(old_estimatedRate) > estimatedRate_threshold:
        print("BTC Alert!")
        old_basis = basis
        old_estimateRate = estimatedRate
        send_email(basis,
                   basis_threshold,
                   orderBookFuture['bids'][0][0],
                   orderBookStock['bids'][0][0],
                   fundingRate['funding_rate'],
                   estimatedRate,
                   estimatedRate_threshold)
    print(basis)
