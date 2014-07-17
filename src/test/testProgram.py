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

from program  import Program
from unittest import TestCase, main


class MockServer:
  def accounts(self):
    return [{
        'accountId': 1815754,
        'accountName': 'Primary',
        'accountCurrency': 'EUR',
        'marginRate': 0.05,
      }]


  def instruments(self, account_id, currencies):
    return [{
        'instrument': 'XAU_USD',
        'displayName': 'Gold',
        'pip': '0.01',
        'maxTradeUnits': 1000,
      }]


  def trades(self, account_id):
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


if __name__ == '__main__':
  # enable buffering of output so that in the successful case we do not see any of the messages
  # printed by default (the listed accounts, for instance)
  main(buffer=True)
