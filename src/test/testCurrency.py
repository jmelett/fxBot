# testCurrency.py

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

from currency import Currency
from datetime import datetime, timedelta
from unittest import TestCase, main
from mock     import patch


class MockServer:
  def __init__(self):
    """Create a new MockServer object.

      MockServer is used to virtualize the server objects designed for communication with OANDA's
      servers in a way to just return predefined values.
    """
    self.__disabled = False
    self.__history = {}
    self.__history['S30'] = []
    self.__history['S5'] = [
      {'complete': True, 'closeMid': 1338.3945, 'highMid': 1338.432, 'lowMid': 1338.3945,
       'volume': 6, 'openMid': 1338.432, 'time': '2014-07-12T22:25:05.000000Z'},
      {'complete': True, 'closeMid': 1338.325, 'highMid': 1338.355, 'lowMid': 1338.325,
       'volume': 5, 'openMid': 1338.355, 'time': '2014-07-12T22:25:10.000000Z'},
      {'complete': False, 'closeMid': 1338.3435, 'highMid': 1338.3635, 'lowMid': 1338.325,
       'volume': 9, 'openMid': 1338.325, 'time': '2014-07-12T22:25:15.000000Z'}
    ]


  def history(self, currency, granularity, count):
    if self.__disabled:
      return []

    if currency == "XAU_USD":
      values = self.__history[granularity]
      return values[len(values) - count:len(values)]

    assert False
    return None


  def disable(self):
    """Disable the server object to just return an empty list on every incocation of history()."""
    self.__disabled = True


  def enable(self):
    """Enable the server object to actually return historical data."""
    self.__disabled = False


class TestCurrency(TestCase):
  def setUp(self):
    self.__server = MockServer()
    self.__currencyName = 'XAU_USD'
    self.__currency = Currency(self.__server, self.__currencyName)


  def testHistory(self):
    """Test normal history retrieval from a server and verify intended order of values."""
    history = self.__currency.history('5s', 1)
    self.assertEqual(len(history), 1)
    self.assertEqual(history[0]['time'], datetime(2014, 7, 12, 22, 25, 15))

    history = self.__currency.history('5s', 2)
    self.assertEqual(len(history), 2)
    self.assertEqual(history[0]['time'], datetime(2014, 7, 12, 22, 25, 15))
    self.assertEqual(history[1]['time'], datetime(2014, 7, 12, 22, 25, 10))


  def testHistoryCachingCount(self):
    """Verify that historical data is cached and if more data is requested a new request is made."""
    # fix the date returned to make the test work even in the worst scheduling scenarios
    with patch('currency.datetime') as mockNow:
      mockNow.now.return_value = datetime.now()

      history = self.__currency.history('5s', 2)
      self.assertEqual(len(history), 2)

      self.__server.disable()
      self.assertEqual(self.__server.history(self.__currencyName, 'S5', 2), [])

      # should still succeed since we get the cached value
      history = self.__currency.history('5s', 2)
      self.assertEqual(len(history), 2)

      # when we request more data the cache must not be used and the server will only return an empty
      # list
      history = self.__currency.history('5s', 3)
      self.assertEqual(history, [])


  def testHistoryCachingTime(self):
    """Verify that historical data is cached but if time advances a new request is made."""
    now = datetime.now()

    with patch('currency.datetime') as mockNow:
      mockNow.now.return_value = now

      history = self.__currency.history('5s', 2)
      self.assertEqual(len(history), 2)

    self.__server.disable()
    self.assertEqual(self.__server.history(self.__currencyName, 'S5', 2), [])

    with patch('currency.datetime') as mockNow:
      # advance wallclock time by 2s -- we are within the granularity so the cache is still
      # considered up-to-date
      mockNow.now.return_value = now + timedelta(seconds=2)

      history = self.__currency.history('5s', 2)
      self.assertEqual(len(history), 2)

    with patch('currency.datetime') as mockNow:
      # advance wallclock time by 5 seconds -- we are outside of our granularity so the currency
      # should know that it needs to fetch new data from the server
      mockNow.now.return_value = now + timedelta(seconds=5)

      history = self.__currency.history('5s', 2)
      self.assertEqual(history, [])

    # reenable the server again
    self.__server.enable()
    history = self.__server.history(self.__currencyName, 'S5', 2)
    self.assertEqual(len(history), 2)

    with patch('currency.datetime') as mockNow:
      # now we are within the granularity again but the cached history no longer contains enough
      # elements (because the last request returned an empty list)
      mockNow.now.return_value = now + timedelta(seconds=2)

      history = self.__currency.history('5s', 2)
      self.assertEqual(len(history), 2)


  def testHistoryCachingGranularity(self):
    """Verify that historical data is cached but on a granularity basis."""
    with patch('currency.datetime') as mockNow:
      mockNow.now.return_value = datetime.now()

      history = self.__currency.history('5s', 2)
      self.assertEqual(len(history), 2)

      history = self.__currency.history('30s', 2)
      self.assertEqual(history, [])

      self.__server.disable()

      # must return cached value
      history = self.__currency.history('5s', 2)
      self.assertEqual(len(history), 2)


if __name__ == '__main__':
  main()
