# 比特币期货交易
合约套利交易/交易回测提醒

套利交易选择了okex的季度合约和binance的永续合约，为什么呢？
1. 选择okex季度合约的原因
交易量数一数二，而且插针严重，经常发疯。这就是套利最喜欢的地方。taker手续费万5，虽然高一点，但是只能接受。
2. 选择binance永续合约的原因
手续费业内最低taker是万2.88，需要用推广账户和BNB支付手续费。

运行`./spread`之前, 配置`config.json`
1. 设置自己的`API KEY`。
2. 配置交易的细节参数比如一次交易最大多少，最少多少之类。
3. 如果因为国内限制访问不了binance，可以配置 proxy，比如ss协议。
