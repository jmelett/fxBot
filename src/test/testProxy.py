# testProxy.py

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

from proxy    import createProxyInstance
from unittest import TestCase, main


class MockServer:
  def currentPrices(self, currency):
    return 'Server'


class MockProxy1:
  def __init__(self, server):
    super().__init__(server)

  def currentPrices(self, currency):
    return 'Proxy1' + super().currentPrices(currency)

  def history(self, currency, granularity, count):
    return str(currency) + str(granularity) + str(count)


class MockProxy2:
  def __init__(self, server):
    super().__init__(server)

  def currentPrices(self, currency):
    return 'Proxy2' + super().currentPrices(currency)


class TestCacheProxy(TestCase):
  def setUp(self):
    self.__server = MockServer()
    self.__proxy = createProxyInstance(self.__server, MockProxy1, MockProxy2)


  def testOrdering(self):
    """Verify that the order of invocations is as intended."""
    # MockProxy1 should execute first, then MockProxy2, and the MockServer should be last
    result = self.__proxy.currentPrices('XAU_USD')
    self.assertEqual(result, 'Proxy1Proxy2Server')


  def testMethodLookup(self):
    """Verify that although no proxy implements this method it is still forwarded to the server."""
    result = self.__proxy.history('XAU_USD', 'S5', 10)
    self.assertEqual(result, 'XAU_USDS510')


if __name__ == '__main__':
  main()
