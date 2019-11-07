#!/usr/bin/env python3
import json
import sys
import time
import ccxt
import smtplib
import os

from email.mime.text import MIMEText
from email.header import Header

sender = 'fabius8@aliyun.com'
receivers = ['fabius888@163.com']
auth = json.load(open("auth.json"))


from datetime import datetime
#timestr = '2019-10-10 15:33:00'
#datetime_obj = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
#stamp = int(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)

def beep():
    print("\a\a\a\a\a")
    time.sleep(1)
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
        subject = "okex basis " + str(basis) + " price " + str(futurePrice)
        smtpObj = smtplib.SMTP_SSL('smtp.aliyun.com', 465)
        # smtpObj.set_debuglevel(1)
        smtpObj.login(auth['username'], auth['password'])
        message['Subject'] = subject
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        smtpObj.close()
    except smtplib.SMTPException as e:
        print("Send Mail Fail", e)
    time.sleep(300)


config = json.load(open('config.json'))
Base = config["Base"]
Quote = config["Quote"]
Contract = config["Contract"]
futurePair = Base + '-' + Quote
stockPair = Base + '/' + 'USDT'
delay = 5
# 10% price change
basis_threshold = 0.20
old_basis = -1
estimatedRate_threshold = 0.20
old_estimatedRate = -1

exchange = ccxt.okex3(config["okex"])
exchange.load_markets()
for symbol in exchange.markets:
    if futurePair in symbol:
        market = exchange.markets[symbol]
        if market['info']['alias'] == 'quarter':
            futurePair = market['symbol']
            break

n = 10

while True:
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    time.sleep(delay)
    try:
        fundingRate = exchange.swapGetInstrumentsInstrumentIdFundingTime({'instrument_id': 'BTC-USD-SWAP'})
        estimatedRate = float(int(float(fundingRate['estimated_rate'])*100000))/100000
        bars = exchange.fetch_ohlcv(futurePair, '15m', None, n)
    except Exception as result:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "oops... restarting0", result)
        continue

    isfound = 1

    for i in range(0, n-1):
        print("volume:", bars[n-1][5], bars[n-2-i][5])
        if bars[n-1][5] < bars[n-2-i][5]:
            isfound = 0
            break
        #print(bars[n-1])
        #print(bars[n-2-i])
        #if (not (bars[n-1][2] > bars[n-2-i][2] and bars[n-1][4] < bars[n-1][1])) and (not (bars[n-1][3] < bars[n-2-i][3] and bars[n-1][4] > bars[n-1][1])):
        #    isfound = 0
        #    break

    if old_estimatedRate == -1 or old_estimatedRate == 0:
        old_estimatedRate = estimatedRate
    try:
        orderBookFuture = exchange.fetch_order_book(futurePair)
        orderBookStock = exchange.fetch_order_book(stockPair)
    except Exception as result:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "oops... restarting1", result)
        continue

    basis = orderBookFuture['bids'][0][0] - orderBookStock['bids'][0][0]
    basis = int(basis)
    if old_basis == -1 or old_basis == 0:
        old_basis = basis

    try:
        if old_basis != 0:
            basis_change = (basis - old_basis) / old_basis
        else:
            basis_change = 0
        if old_estimatedRate != 0:
            estimatedRate_change = (estimatedRate - old_estimatedRate) / old_estimatedRate
        else:
            estimatedRate_change = 0
    except Exception as result:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "oops... restarting", result)
        continue

    print("future price: ", orderBookFuture['bids'][0][0])
    print(old_basis, basis)
    print("basis change", basis_change * 100, "%")
    print(old_estimatedRate, estimatedRate)
    print("estimatedRate change ", estimatedRate_change * 100, "%")
    print(" ")

    #if abs(basis_change) > basis_threshold or abs(estimatedRate_change) > estimatedRate_threshold or isfound == 1:
    if isfound == 1:
        os.system("say big volume")
        beep()
        try:
            send_email(basis,
                       basis_threshold,
                       orderBookFuture['bids'][0][0],
                       orderBookStock['bids'][0][0],
                       fundingRate['funding_rate'],
                       estimatedRate,
                       estimatedRate_threshold)
        except Exception as result:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "oops... restarting", result)
            continue

        old_basis = basis
        old_estimatedRate = estimatedRate
