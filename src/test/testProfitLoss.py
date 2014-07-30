# testProfitLoss.py

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

from trade    import profitLossRaw, profitLossRawWithHome
from currency import Currency
from datetime import datetime, timedelta
from unittest import TestCase, main
from decimal  import Decimal
from mock     import patch


class MockServer:
  def __init__(self, ask_price, bid_price):
    """Create a new MockServer object.

      MockServer is used to virtualize the server objects designed for communication with OANDA's
      servers in a way to just return predefined values.
    """
    self.__ask_price = ask_price
    self.__bid_price = bid_price


  def currentPrices(self, currency):
    return {
      'instrument': 'XAU_USD',
      'time': formatDate(datetime.now()),
      'ask': self.__ask_price,
      'bid': self.__bid_price,
    }


  def askPrice(self, ask_price):
    """Set an ask price to return on next currentPrices() invocation.

      Parameters:
        ask_price  String specifying the ask price to set.
    """
    self.__ask_price = ask_price


  def bidPrice(self, bid_price):
    """Set a bid price to return on next currentPrices() invocation.

      Parameters:
        bid_price  String specifying the bid price to set.
    """
    self.__bid_price = bid_price


class TestProfitLoss(TestCase):
  #def setUp(self):
  #  self.__server = MockServer()


  def testProfitLossRaw(self):
    """Test profit calculation in quoted currency."""
    # Home Currency: EUR
    # Currency Pair: EUR/USD
    # Base = EUR
    # Quote = USD
    # Quote/Home Currency = USD/EUR = 0.9505
    # Opening Rate = 0.9517
    # Closing Rate = 0.9505
    # Units = 10000
    open_rate = Decimal('0.9517')
    close_rate = Decimal('0.9505')
    units = 10000
    profit = profitLossRaw(open_rate, close_rate, units)

    self.assertEqual(profit, Decimal('-12.00'))


  def testProfitLossRawWithHome(self):
    """Test profit with conversion into home rate."""
    # Home Currency: USD
    # Currency Pair: GBP/CHF
    # Base = GBP
    # Quote = CHF
    # Quote/Home Currency = CHF/USD = 1.1025
    # Opening Rate = 2.1443
    # Closing Rate = 2.1452
    # Units = 1000
    open_rate = Decimal('2.1443')
    close_rate = Decimal('2.1452')
    quote_home_rate = Decimal('1.1025')
    units = 1000
    profit = profitLossRawWithHome(open_rate, close_rate, quote_home_rate, units)

    self.assertEqual(profit, Decimal('0.99225'))



  #def testLongLoss(self):
  #  """Test profit calculation for loss on long position."""
  #  # You see that the rate for USD/JPY is 115.00/05 and decide to buy 10,000 USD. Your trade is
  #  # executed at 115.05.
  #  # 10,000 USD * 115.05 = 1,150,500 JPY
  #  # You bought 10,000 USD and sold 1,150,500 JPY.
  #  # The market rate of USD/JPY falls to 114.45/50. You decide to sell back 10,000 USD at 114.45.
  #  # 10,000 USD * 114.45 = 1,144,500 JPY
  #  # You bought 10,000 USD for 1,150,500 JPY and sold 10,000 USD back for 1,144,500 JPY. The
  #  # difference is your loss and is calculated as follows: 1,150,500 - 1,144,500 = 6,000 JPY. Note
  #  # that your loss is in JPY and must be converted back to dollars.
  #  # To calculate this amount in USD:
  #  # 6,000 JPY / 114.45 = 52.42 USD or 6,000 * 1/114.45 = 52.42 USD
  #  self.__server.bid('115.00')
  #  self.__server.ask('115.05')

  #  currency = Currency(self.__server, 'USD_JPY')

  #  self.__server.bid('114.45')
  #  self.__server.ask('114.50')

    # You see that the rate for EUR/USD is 0.9517/22 and decide to sell 10,000 EUR. Your trade is
    # executed at 0.9517.
    # 10,000 EUR * 0.9517 = 9,517.00 USD
    # You sold 10,000 EUR and bought 9,517.00 USD.
    # After you trade, the market rate of EUR/USD decreases to EUR/USD = 0.9500/05. You then buy
    # back 10,000 EUR at 0.9505.
    # 10,000 EUR * 0.9505 = 9,505.00 USD
    # You sold 10,000 EUR for 9,517 USD and bought 10,000 back for 9,505. The difference is your
    # profit:
    # 9,517.00 - 9,505.00 = 12.00 USD
    #currency = Currency(self.__server, 'EUR_USD')

    #self.__server.bid('0.9517')
    #self.__server.ask('0.9539')
    #buy_price = currency.currentPrices()

    #self.__server.bid('0.9500')
    #self.__server.ask('0.9505')
    #current_price = currency.currentPrices()

    #self.assertEqual(profitLoss(10000, buy_price, current_price, True), Decimal(12.000))


if __name__ == '__main__':
  main()
