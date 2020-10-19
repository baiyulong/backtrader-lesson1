from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime
import os.path
import sys

import backtrader as bt


class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        dt = dt or self.data0.datetime.date(0)
        print('%s, %s' % (dt, txt))

    def __init__(self):
        self.dataclose = self.data0.close
        self.order = None
        self.bar_executed = 0

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed += len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected.')

        self.order = None

    def next(self):

        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        if not self.position:

            if self.dataclose[0] > self.dataclose[-1]:
                if self.dataclose[-1] > self.dataclose[-2]:
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.order = self.buy()

            else:

                if len(self) >= (self.bar_executed + 5):
                    self.log('SELL CREATED, %.2f', self.dataclose[0])
                    self.order = self.sell()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cerebro = bt.Cerebro()

    cerebro.addstrategy(TestStrategy)

    mod_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    data_path = os.path.join(mod_path, 'symbols/600036.SS.csv')

    data = bt.feeds.YahooFinanceCSVData(
        dataname=data_path,
        fromdate=datetime.datetime(2019, 1, 1),
        todate=datetime.datetime(2020, 10, 18)
    )

    cerebro.adddata(data)

    cerebro.broker.set_cash(100.00)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
