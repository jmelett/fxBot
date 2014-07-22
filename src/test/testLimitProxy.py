# testLimitProxy.py

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
from limitProxy import LimitProxy
from unittest   import TestCase, main
from mock       import patch, MagicMock


class MockTime:
  def __init__(self, value):
    self.__value = value
    self.__slept = 0


  def __call__(self):
    return self.__value


  def sleep(self, *args, count=1):
    """Simulate a sleep.

      Parameters:
        count  Number of times to sleep in a granularity of 0.1s (i.e., a count of 10 simulates
               sleeping one second).
    """
    self.__value += 0.1
    self.__slept += 1


  def slept(self):
    return self.__slept


class TestLimitProxy(TestCase):
  def setUp(self):
    self.__server = MagicMock()
    self.__proxy = createProxyInstance(self.__server, LimitProxy)


  def testLimit(self):
    with patch('limitProxy.time') as mock_time:
      with patch('limitProxy.sleep') as mock_sleep:
        time = MockTime(1.0)
        # an invocation of limitProxy.time returns the value of the MockTime object
        mock_time.side_effect = time
        # an invocation of limitProxy.sleep increases the value of the MockTime object by 0.1
        mock_sleep.side_effect = time.sleep

        self.__proxy.currentPrices(self, 'XAU_USD')
        self.__proxy.currentPrices(self, 'XAU_USD')
        self.__proxy.currentPrices(self, 'XAU_USD')
        self.__proxy.currentPrices(self, 'XAU_USD')
        self.assertEqual(time.slept(), 0)
        self.__proxy.currentPrices(self, 'XAU_USD')
        self.assertEqual(time.slept(), 10)

        self.assertEqual(self.__server.currentPrices.call_count, 5)


  def testLimitWithSleep(self):
    with patch('limitProxy.time') as mock_time:
      with patch('limitProxy.sleep') as mock_sleep:
        time = MockTime(1.0)
        mock_time.side_effect = time
        mock_sleep.side_effect = time.sleep

        self.__proxy.currentPrices(self, 'XAU_USD')
        time.sleep()
        self.__proxy.instruments(self, '1815754', 'XAU_USD')
        time.sleep()
        self.__proxy.currentPrices(self, 'XAU_USD')
        time.sleep()

        self.__proxy.trades(self, '1815754')
        self.assertEqual(time.slept(), 3)
        self.__proxy.accounts(self)
        self.assertEqual(time.slept(), 10)
        self.__proxy.history('XAU_USD', 'S5', 10)
        self.assertEqual(time.slept(), 11)
        self.__proxy.currentPrices(self, 'XAU_USD')
        self.assertEqual(time.slept(), 12)
        self.__proxy.instruments(self, '1815754', 'XAU_USD')
        self.assertEqual(time.slept(), 13)
        self.__proxy.trades(self, '1815754')
        self.assertEqual(time.slept(), 20)

        self.assertEqual(self.__server.currentPrices.call_count, 3)
        self.assertEqual(self.__server.instruments.call_count, 2)
        self.assertEqual(self.__server.accounts.call_count, 1)
        self.assertEqual(self.__server.history.call_count, 1)
        self.assertEqual(self.__server.trades.call_count, 2)


if __name__ == '__main__':
  main()
