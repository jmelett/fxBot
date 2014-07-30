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
from unittest import TestCase, main
from decimal  import Decimal


class TestProfitLoss(TestCase):
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


if __name__ == '__main__':
  main()
