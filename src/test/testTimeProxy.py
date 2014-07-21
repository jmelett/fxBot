# testTimeProxy.py

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

from datetime        import datetime
from datetimeRfc3339 import formatDate
from proxy           import createProxyInstance
from timeProxy       import TimeProxy
from unittest        import TestCase, main
from mock            import patch


class MockServer:
  def __init__(self):
    self.__current_time = None
    self.__complete = False


  def currentTime(self, time):
    self.__current_time = time


  def complete(self, complete):
    self.__complete = complete


  def currentPrices(self, currency):
    """Retrieve the current bid and ask prices for a currency."""
    return {
      'instrument': 'XAU_USD',
      'time': formatDate(self.__current_time),
      'ask': 1339.211,
      'bid': 1336.661,
    }


  def history(self, currency, granularity, count):
    return [{
      'time': formatDate(self.__current_time),
      'openMid': 1.36803,
      'highMid': 1.368125,
      'lowMid': 1.364275,
      'closeMid': 1.365315,
      'volume': 28242,
      'complete': self.__complete,
    }]


class TestTimeProxy(TestCase):
  def setUp(self):
    self.__server = MockServer()
    self.__proxy = createProxyInstance(self.__server, TimeProxy)


  def testNoTime(self):
    """Verify that the estimated time is None in case no estimation can be made."""
    self.assertIsNone(self.__proxy.estimatedTime())


  def testCurrentPricesNoDelta(self):
    # first test is to set the server's time to the same as the local time
    now = datetime.now()
    with patch('timeProxy.datetime') as mock_now:
      mock_now.now.return_value = now

      self.__server.currentTime(now)
      self.__proxy.currentPrices('XAU_USD')
      self.assertEqual(self.__proxy.estimatedTime(), now)


  def testCurrentPricesWithDeltaBefore(self):
    local_now = datetime(2014, 7, 20, 20)
    server_now = datetime(2014, 7, 20, 18)

    with patch('timeProxy.datetime') as mock_now:
      mock_now.now.return_value = local_now

      self.__server.currentTime(server_now)
      self.__proxy.currentPrices('XAU_USD')

      self.assertEqual(self.__proxy.estimatedTime(), server_now)


  def testCurrentPricesMultiple(self):
    local_now_1     = datetime(2014, 7, 20, 20, 0, 10)
    server_now_1    = datetime(2014, 7, 20, 22, 0, 30)
    local_now_2     = datetime(2014, 7, 20, 20, 0, 20)
    server_now_2    = datetime(2014, 7, 20, 22, 0, 36)
    local_now_3     = datetime(2014, 7, 20, 20, 0, 40)
    server_expected = datetime(2014, 7, 20, 22, 0, 58)

    with patch('timeProxy.datetime') as mock_now:
      mock_now.now.return_value = local_now_1
      self.__server.currentTime(server_now_1)
      self.__proxy.currentPrices('XAU_USD')

    with patch('timeProxy.datetime') as mock_now:
      mock_now.now.return_value = local_now_2
      self.__server.currentTime(server_now_2)
      self.__proxy.currentPrices('XAU_USD')

    with patch('timeProxy.datetime') as mock_now:
      mock_now.now.return_value = local_now_3

      self.assertEqual(self.__proxy.estimatedTime(), server_expected)


  def testHistoryNotComplete(self):
    now = datetime.now()
    with patch('timeProxy.datetime') as mock_now:
      mock_now.now.return_value = now

      self.__server.currentTime(now)
      self.__proxy.history('XAU_USD', '5s', 10)
      self.assertEqual(self.__proxy.estimatedTime(), now)


  def testHistoryComplete(self):
    now = datetime.now()
    with patch('timeProxy.datetime') as mock_now:
      mock_now.now.return_value = now

      self.__server.currentTime(now)
      self.__server.complete(True)
      self.__proxy.history('XAU_USD', '5s', 10)
      self.assertIsNone(self.__proxy.estimatedTime())


if __name__ == '__main__':
  main()
