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
from datetime import datetime
from unittest import TestCase, main


class MockServer:
  def __init__(self):
    """Create a new MockServer object.

      MockServer is used to virtualize the server objects designed for communication with OANDA's
      servers in a way to just return predefined values.
    """
    self.__history = {}
    self.__history['S5'] = [
      {'complete': True, 'closeMid': 1338.3945, 'highMid': 1338.432, 'lowMid': 1338.3945,
       'volume': 6, 'openMid': 1338.432, 'time': '2014-07-12T22:25:05.000000Z'},
      {'complete': True, 'closeMid': 1338.325, 'highMid': 1338.355, 'lowMid': 1338.325,
       'volume': 5, 'openMid': 1338.355, 'time': '2014-07-12T22:25:10.000000Z'},
      {'complete': False, 'closeMid': 1338.3435, 'highMid': 1338.3635, 'lowMid': 1338.325,
       'volume': 9, 'openMid': 1338.325, 'time': '2014-07-12T22:25:15.000000Z'}
    ]


  def history(self, currency, granularity, count):
    if currency == "XAU_USD":
      values = self.__history[granularity]
      return values[len(values) - count:len(values)]

    assert False
    return None


class TestCurrency(TestCase):
  def setUp(self):
    self.__server = MockServer()
    self.__currency = Currency(self.__server, 'XAU_USD')


  def testHistory(self):
    """Test normal history retrieval from a server and verify intended order of values."""
    history = self.__currency.history('5s', 1)
    self.assertEqual(len(history), 1)
    self.assertEqual(history[0]['time'], datetime(2014, 7, 12, 22, 25, 15))

    history = self.__currency.history('5s', 2)
    self.assertEqual(len(history), 2)
    self.assertEqual(history[0]['time'], datetime(2014, 7, 12, 22, 25, 15))
    self.assertEqual(history[1]['time'], datetime(2014, 7, 12, 22, 25, 10))


if __name__ == '__main__':
  main()
