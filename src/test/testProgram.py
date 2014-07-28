# testProgram.py

#/***************************************************************************
# *   Copyright (C) 2014 Daniel Mueller                                     *
# *                                                                         *
# *   This program is free software: you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation, either version 3 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU General Public License for more details.                          *
# *                                                                         *
# *   You should have received a copy of the GNU General Public License     *
# *   along with this program.  If not, see <http://www.gnu.org/licenses/>. *
# ***************************************************************************/

from price     import Price
from program   import Program
from decimal   import Decimal
from time      import sleep
from datetime  import datetime
from threading import Thread, Event
from unittest  import TestCase, main
from mock      import patch


class MockServer:
  def token(self):
    """Dummy implementation for the token() method of a real server."""
    return 'XXXXXXXXXX'


  def currentPrices(self, currency):
    """Dummy implementation for the currentPrices() method of a real server."""
    return {
        'instrument': 'XAU_USD',
        'time': '2014-07-11T20:59:58.718193Z',
        'ask': 1339.211,
        'bid': 1336.661,
      }


  def history(self, currency, granularity, count):
    return [{
        'time': '2014-07-02T00:00:00.000000Z',
        'openMid': 1.36803,
        'highMid': 1.368125,
        'lowMid': 1.364275,
        'closeMid': 1.365315,
        'volume': 28242,
        'complete': True,
      }]


  def accounts(self):
    """Dummy implementation for the accounts() method of a real server."""
    return [{
        'accountId': 1815754,
        'accountName': 'Primary',
        'accountCurrency': 'EUR',
        'marginRate': 0.05,
      }]


  def instruments(self, account_id, currencies):
    """Dummy implementation for the instruments() method of a real server."""
    return [{
        'instrument': 'XAU_USD',
        'displayName': 'Gold',
        'pip': '0.01',
        'maxTradeUnits': 1000,
      }]


  def trades(self, account_id):
    """Dummy implementation for the trades() method of a real server."""
    return [{
        'id': 612021234,
        'time': '2014-07-14T17:21:26.000000Z',
        'instrument': 'USB05Y_USD',
        'units': 80,
        'side': 'sell',
        'price': 119.895,
        'stopLoss': 120.15,
        'takeProfit': 119.4,
        'trailingStop': 0,
        'trailingAmount': 0,
      }]


class MockStreamer(Thread):
  def __init__(self, token, queue):
    super().__init__()
    self._destroy = Event()
    self._queue = queue


  def start(self, *args, **kwargs):
    Thread.start(self)


  def disconnect(self):
    self._destroy.set()


class MockRateStreamer(MockStreamer):
  def run(self):
    i = 0
    while not self._destroy.is_set():
      if i % 2 == 0:
        self._queue.put({
          'instrument': 'XAU_USD',
          'time': '2014-07-09T00:00:00.000000Z',
          'ask':  '0.1111111',
          'bid':  '0.1111110',
        })
      else:
        self._queue.put({
          'instrument': 'XAU_USD',
          'time': datetime(2014, 7, 9, 12, 0, 0, 0),
          'ask':  Price(Decimal('0.1111111'), Decimal('0.001')),
          'bid':  Price(Decimal('0.1111110'), Decimal('0.001')),
          'parsed': True,
        })

      i = i + 1
      sleep(0)


class MockEventStreamer(MockStreamer):
  def run(self):
    i = 0
    while not self._destroy.is_set():
      if i % 10 != 0:
        self._queue.put({'transaction': {
          'tradeId': 615670377, 'accountBalance': 99959.6797, 'price': 173.366, 'side': 'buy',
          'instrument': 'GBP_JPY', 'interest': -0.0522, 'time': '2014-07-17T18:57:05.000000Z',
          'units': 4000, 'type': 'TRAILING_STOP_FILLED', 'id': 615936867, 'pl': 12.844,
          'accountId': 1815754
        }})
      else:
        self._queue.put({'heartbeat': {'time': '2014-07-09T00:00:00.000000Z'}})

      i = i + 1
      sleep(0)


class TestProgram(TestCase):
  def setUp(self):
    self.__server = MockServer()
    self.__program = Program(self.__server)


  def testListAccounts(self):
    self.__program.listAccounts()


  def testListCurrencies(self):
    self.__program.listCurrencies('1815754')


  def testListTrades(self):
    self.__program.listTrades('1815754')


  @patch('program.RateStreamer', MockRateStreamer)
  @patch('program.EventStreamer', MockEventStreamer)
  def testRun(self):
    """Test main infrastructure of the program.

      Notes:
        This test aimes at executing the majority of paths in the application's main loop.
    """
    try:
      self.__program.start('1815754', 'XAU_USD', 0)
      # hammer events on the application for one second and quit
      sleep(1)
      self.__program.destroy()
    except KeyboardInterrupt:
      self.__program.destroy()
      self.fail('Interrupted')


if __name__ == '__main__':
  # workaround for problem:
  # "ImportError: Failed to import _strptime because the import lockis held by another thread."
  from datetime import datetime
  datetime.strptime('2012-01-01', '%Y-%m-%d')

  # enable buffering of output so that in the successful case we do not see any of the messages
  # printed by default (the listed accounts, for instance)
  main(buffer=True)
