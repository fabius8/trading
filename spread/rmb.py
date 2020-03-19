import requests
import time
from collections import Counter
import json
import random


user_agent = [
    "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)", 
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)", 
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)", 
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)", 
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)", 
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)", 
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)", 
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)", 
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)", 
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6", 
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1", 
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0", 
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5", 
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6", 
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11", 
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20", 
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"
] 

HEADER = { 
'User-Agent': random.choice(user_agent),  # 浏览器头部
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', # 客户端能够接收的内容类型
'Accept-Language': 'en-US,en;q=0.5', # 浏览器可接受的语言
'Connection': 'keep-alive', # 表示是否需要持久连接
} 

ok_url = "https://www.okex.me/v3/c2c/tradingOrders/book"
binance_url = "https://c2c.binance-cn.com/gateway-api/v2/public/c2c/adv/search"
huobi_url = "https://otc-api-hk.eiijo.cn/v1/data/trade-market"

while True:
    print("="*40)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    try:
        # OKEX
        prices = []

        r = requests.get(url=ok_url, headers=HEADER,
                         params={'t': '1581768737354',
                                 'side': 'sell',
                                 'baseCurrency': 'usdt',
                                 'quoteCurrency': 'cny',
                                 'userType': 'certified',
                                 'paymentMethod': 'all'},
                         timeout=5)
        print("OKEX     buy: ", r.json()['data']['sell'][0]['price'])


        time.sleep(3)
        r = requests.get(url=ok_url, headers=HEADER,
                         params={'t': '1581768737354',
                                 'side': 'buy',
                                 'baseCurrency': 'usdt',
                                 'quoteCurrency': 'cny',
                                 'userType': 'certified',
                                 'paymentMethod': 'all'},
                         timeout=5)
        print("OKEX    sell: ", r.json()['data']['buy'][0]['price'])

        # binance
        headers = {"Content-Type": "application/json"}
        data = json.dumps({"page":1,"rows":10,"fiat":"CNY","asset":"USDT","tradeType":"BUY"})
        r = requests.post(url=binance_url, headers=headers,
                          data=data,
                          timeout=5)
        print("Binance  buy: ", r.json()['data'][0]['advDetail']['price'])

        data = json.dumps({"page":1,"rows":10,"fiat":"CNY","asset":"USDT","tradeType":"SELL"})
        r = requests.post(url=binance_url, headers=headers,
                          data=data,
                          timeout=5)
        print("Binance sell: ", r.json()['data'][0]['advDetail']['price'])
        # huobi
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        r = requests.get(url=huobi_url, headers=headers,
                         params={'coinId': '2',
                                 'currency': '1',
                                 'tradeType': 'buy',
                                 'currPage': '1',
                                 'payMethod': '0',
                                 'country': '37',
                                 'blockType': 'general',
                                 'online': '1',
                                 'range': '0',
                                 'amount': ''},
                         timeout=5)
        print("huobi    buy: ", r.json()['data'][0]['price'])

        headers = {"Content-Type": "application/json;charset=UTF-8"}
        r = requests.get(url=huobi_url, headers=headers,
                         params={'coinId': '2',
                                 'currency': '1',
                                 'tradeType': 'sell',
                                 'currPage': '1',
                                 'payMethod': '0',
                                 'country': '37',
                                 'blockType': 'general',
                                 'online': '1',
                                 'range': '0',
                                 'amount': ''},
                         timeout=5)
        print("huobi   sell: ", r.json()['data'][0]['price'])
    except Exception as err:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), err)
        time.sleep(60)
        continue
    time.sleep(60*5)
