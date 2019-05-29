#!/usr/bin/env python3
import jqdatasdk
import time
import json
import smtplib
from email.mime.text import MIMEText
sender = 'fabius8@aliyun.com'
receivers = ['fabius888@163.com']

cds = json.load(open("jq_config.json"))
auth = json.load(open("auth.json"))
jqdatasdk.auth(cds['account'], cds['password'])
futures = jqdatasdk.get_all_securities(['futures'])

dom_futures = []
for i in futures.index:
    if i.find('9999') != -1:
        dom_futures.append(i)

g_report = {}
g_report_interval = {}
for i in dom_futures:
    g_report[i] = 0
    g_report_interval[i] = 240


def ATR(highs, lows, closes):
    high_to_low = highs - lows
    high_to_prev_close = abs(highs[1:] - closes[:-1])
    low_to_prev_close = abs(lows[1:] - closes[:-1])
    TR = high_to_low.combine(high_to_prev_close,
                             max,
                             fill_value=0).combine(low_to_prev_close,
                                                   max,
                                                   fill_value=0)
    return TR.sum() / TR.count()


def send_email(stock, indicator, freq, price, highest, lowest, N,
               positionSizePercent, positionSize):
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
    message['To'] = ",".join(receivers)
    try:
        if indicator == "LONG":
            subject = str(stock) + " " + indicator
        elif indicator == "SHORT":
            subject = str(stock) + " " + indicator
        smtpObj = smtplib.SMTP_SSL('smtp.aliyun.com', 465)
        # smtpObj.set_debuglevel(1)
        smtpObj.login(auth['username'], auth['password'])
        message['Subject'] = subject
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
        smtpObj.close()
    except smtplib.SMTPException as e:
        print("Send Mail Fail", e)

    g_report[stock] = 1
    g_report_interval[stock] = 240


def monitor():
    window = 20

    for i in dom_futures:
        if g_report[i] == 1 and g_report_interval[i] == 0:
            g_report[i] = 0
        if g_report[i] == 1 and g_report_interval[i] > 0:
            g_report_interval[i] -= 1
            continue

        df = jqdatasdk.get_bars(i,
                                window + 1,
                                unit='1d',
                                fields=['date', 'open', 'high', 'low', 'close'],
                                include_now=True, end_dt=None)

        if len(df) < 21:
            continue
        price = df['close'][20]
        N = ATR(df['high'][1:20], df['low'][1:20], df['close'][1:20])
        highest = df['high'][0:19].max()
        lowest = df['low'][0:19].min()
        print(i, price, highest, lowest)
        positionSizePercent = price / N
        positionSize = 10000 * 0.01 / N
        if price > highest:
            indicator = "LONG"
            send_email(i, indicator, "1d",
                       price, highest, lowest, N,
                       positionSizePercent, positionSize)
        elif price < lowest:
            indicator = "SHORT"
            send_email(i, indicator, "1d",
                       price, highest, lowest, N,
                       positionSizePercent, positionSize)


if __name__ == '__main__':
    while True:
        monitor()
        time.sleep(60)

