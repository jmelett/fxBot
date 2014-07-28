# testCacheTimeProxy.py

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

from proxy      import createProxyInstance
from cacheProxy import CacheProxy
from datetime   import datetime
from unittest   import TestCase, main
from mock       import patch


class MockServer:
  def __init__(self):
    """Create a new MockServer object."""
    self.__time = None
    self.__history = {
      'XAU_USD': {
        'M15': [
          {'time': '2014-07-28T19:30:00.000000Z', 'lowMid': 1487.82,  'highMid': 1488.74,
           'closeMid': 1488.53,  'openMid': 1488.447, 'complete': True, 'volume': 38},
          {'time': '2014-07-28T19:45:00.000000Z', 'lowMid': 1488.61,  'highMid': 1489.252,
           'closeMid': 1488.971, 'openMid': 1488.61,  'complete': True, 'volume': 16},
          {'time': '2014-07-28T20:00:00.000000Z', 'lowMid': 1487.777, 'highMid': 1489.158,
           'closeMid': 1489.041, 'openMid': 1488.863, 'complete': True, 'volume': 34},
          {'time': '2014-07-28T20:15:00.000000Z', 'lowMid': 1488.694, 'highMid': 1489.142,
           'closeMid': 1488.694, 'openMid': 1488.851, 'complete': True, 'volume': 7,},
        ],
        'H1': [
          {'time': '2014-07-28T11:00:00.000000Z', 'lowMid': 1485.07,  'highMid': 1487.32,
           'openMid': 1485.07,  'closeMid': 1486.801, 'complete': True, 'volume': 198},
          {'time': '2014-07-28T12:00:00.000000Z', 'lowMid': 1485.903, 'highMid': 1488.104,
           'openMid': 1486.711, 'closeMid': 1487.237, 'complete': True, 'volume': 296},
          {'time': '2014-07-28T13:00:00.000000Z', 'lowMid': 1484.641, 'highMid': 1488.819,
           'openMid': 1487.11,  'closeMid': 1486.811, 'complete': True, 'volume': 375},
        ]
      }
    }


  def history(self, currency, granularity, count):
    values = self.__history[currency][granularity]

    if granularity == 'H1':
      if self.__time < datetime(2014, 7, 28, 13, 00):
        values = values[0: len(values) - 1]
    elif granularity == 'M15':
      if self.__time < datetime(2014, 7, 28, 20, 15):
        values = values[0: len(values) - 1]
      if self.__time < datetime(2014, 7, 28, 20, 00):
        values = values[0: len(values) - 1]

    return values[len(values) - count:len(values)]


  def time(self, time):
    self.__time = time


class MockTimeProxy:
  def __init__(self, server):
    super().__init__(server)

    self.__server = server
    self.__estimated_time = None


  def feedTime(self, time):
    self.__estimated_time = time
    # directly pass the time to our mock server instance as well
    self.__server.time(time)


  def estimatedTime(self):
    return self.__estimated_time


class TestCacheTimeProxy(TestCase):
  def setUp(self):
    self.__server = MockServer()
    self.__proxy = createProxyInstance(self.__server, CacheProxy, MockTimeProxy)


  def testHistoryCachingWithTimeSource15m(self):
    """Verify that history caching is correct if we estimate the server's time."""
    with patch('cacheProxy.datetime') as mock_now:
      mock_now.now.return_value = datetime(2014, 7, 28, 21, 12)

      self.__proxy.feedTime(datetime(2014, 7, 28, 19, 46))
      history = self.__proxy.history('XAU_USD', 'M15', 2)

      self.assertEqual(len(history), 2)
      self.assertEqual(history[1]['time'], '2014-07-28T19:45:00.000000Z')

    with patch('cacheProxy.datetime') as mock_now:
      mock_now.now.return_value = datetime(2014, 7, 28, 21, 26)

      self.__proxy.feedTime(datetime(2014, 7, 28, 20, 00))
      history = self.__proxy.history('XAU_USD', 'M15', 2)

      self.assertEqual(len(history), 2)
      self.assertEqual(history[1]['time'], '2014-07-28T20:00:00.000000Z')

    with patch('cacheProxy.datetime') as mock_now:
      mock_now.now.return_value = datetime(2014, 7, 28, 22, 1)

      self.__proxy.feedTime(datetime(2014, 7, 28, 20, 35))
      history = self.__proxy.history('XAU_USD', 'M15', 2)

      self.assertEqual(len(history), 2)
      self.assertEqual(history[1]['time'], '2014-07-28T20:15:00.000000Z')


  def testHistoryCachingWithTimeSource1h(self):
    """Verify that history caching is correct if we estimate the server's time."""
    with patch('cacheProxy.datetime') as mock_now:
      mock_now.now.return_value = datetime(2014, 7, 28, 11, 13)

      self.__proxy.feedTime(datetime(2014, 7, 28, 12, 47))
      history = self.__proxy.history('XAU_USD', 'H1', 2)

      self.assertEqual(len(history), 2)
      self.assertEqual(history[1]['time'], '2014-07-28T12:00:00.000000Z')

    with patch('cacheProxy.datetime') as mock_now:
      mock_now.now.return_value = datetime(2014, 7, 28, 11, 20)

      self.__proxy.feedTime(datetime(2014, 7, 28, 12, 54))
      history = self.__proxy.history('XAU_USD', 'H1', 2)

      self.assertEqual(len(history), 2)
      self.assertEqual(history[1]['time'], '2014-07-28T12:00:00.000000Z')

    with patch('cacheProxy.datetime') as mock_now:
      mock_now.now.return_value = datetime(2014, 7, 28, 11, 30)

      self.__proxy.feedTime(datetime(2014, 7, 28, 13, 4))
      history = self.__proxy.history('XAU_USD', 'H1', 2)

      self.assertEqual(len(history), 2)
      self.assertEqual(history[1]['time'], '2014-07-28T13:00:00.000000Z')


if __name__ == '__main__':
  main()
