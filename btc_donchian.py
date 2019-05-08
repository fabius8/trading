"""
Test BTC on binance 4h on Donchian Channel
By fabius8
"""
from catalyst import run_algorithm
import numpy as np
from catalyst.api import record, symbol, order_target_percent
from catalyst.exchange.utils.stats_utils import extract_transactions

import matplotlib.pyplot as plt
import pandas as pd

from logbook import Logger

algo_namespace = 'Danchian channel'
log = Logger(algo_namespace)
ChannelPeriods = 20


def initialize(context):
    context.i = 0
    context.asset = symbol('btc_usdt')
    context.base_price = None


def handle_data(context, data):
    context.i += 1
    if context.i % 240 != 0:
        return

    price = data.current(context.asset, 'price')
    highest = data.history(context.asset,
                           'high',
                           bar_count=ChannelPeriods,
                           frequency="240T")[-21:-1].max()
    lowest = data.history(context.asset,
                          'low',
                          bar_count=ChannelPeriods,
                          frequency="240T")[-21:-1].min()

    if context.base_price is None:
        context.base_price = price
    price_change = (price - context.base_price) / context.base_price

    record(price=price,
           cash=context.portfolio.cash,
           price_change=price_change,
           highest=highest,
           lowest=lowest)
    print(price, highest, lowest)

    pos_amount = context.portfolio.positions[context.asset].amount
    if price > highest and pos_amount == 0:
        # buy
        order_target_percent(context.asset, 1)
    elif price < lowest and pos_amount > 0:
        # sell
        order_target_percent(context.asset, 0)


def analyze(context, perf):
    # Get the quote_currency that was passed as a parameter to the simulation
    exchange = list(context.exchanges.values())[0]
    quote_currency = exchange.quote_currency.upper()

    # First chart: Plot portfolio value using quote_currency
    ax1 = plt.subplot(411)
    perf.loc[:, ['portfolio_value']].plot(ax=ax1)
    ax1.legend_.remove()
    ax1.set_ylabel('Portfolio Value\n({})'.format(quote_currency))
    start, end = ax1.get_ylim()
    ax1.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    # Second chart: Plot asset price, moving averages and buys/sells
    ax2 = plt.subplot(412, sharex=ax1)
    perf.loc[:, ['price', 'highest', 'lowest']].plot(
        ax=ax2,
        label='Price')
    ax2.legend_.remove()
    ax2.set_ylabel('{asset}\n({quote})'.format(
        asset=context.asset.symbol,
        quote=quote_currency
    ))
    start, end = ax2.get_ylim()
    ax2.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    transaction_df = extract_transactions(perf)
    if not transaction_df.empty:
        buy_df = transaction_df[transaction_df['amount'] > 0]
        sell_df = transaction_df[transaction_df['amount'] < 0]
        ax2.scatter(
            buy_df.index.to_pydatetime(),
            perf.loc[buy_df.index, 'price'],
            marker='^',
            s=100,
            c='green',
            label=''
        )
        ax2.scatter(
            sell_df.index.to_pydatetime(),
            perf.loc[sell_df.index, 'price'],
            marker='v',
            s=100,
            c='red',
            label=''
        )

    # Third chart: Compare percentage change between our portfolio
    # and the price of the asset
    ax3 = plt.subplot(413, sharex=ax1)
    perf.loc[:, ['algorithm_period_return', 'price_change']].plot(ax=ax3)
    ax3.legend_.remove()
    ax3.set_ylabel('Percent Change')
    start, end = ax3.get_ylim()
    ax3.yaxis.set_ticks(np.arange(start, end, (end - start) / 5))

    # Fourth chart: Plot our cash
    ax4 = plt.subplot(414, sharex=ax1)
    perf.cash.plot(ax=ax4)
    ax4.set_ylabel('Cash\n({})'.format(quote_currency))
    start, end = ax4.get_ylim()
    ax4.yaxis.set_ticks(np.arange(0, end, end / 5))

    plt.show()

if __name__ == '__main__':
    run_algorithm(
        capital_base=1000,
        data_frequency='minute',
        initialize=initialize,
        handle_data=handle_data,
        analyze=analyze,
        exchange_name='binance',
        algo_namespace='btc_donchian',
        quote_currency='usdt',
        start=pd.to_datetime('2017-11-17', utc=True),
        end=pd.to_datetime('2019-5-5', utc=True),
    )
