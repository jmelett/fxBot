# trade.py

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

# Margin Closeout calculator:
# If the account currency is the same as the base of the currency pair
#
# Buy Position MR = (2mOU) / (2mb + 2mU - U)
# Sell Position MR = (-2mOU) / (2mb - 2mU -U)
#
# Account currency is the same as the quote of the currency pair
#
# Buy Position MR = (2m(OU - b)) / U(2m-1)
# Sell Position MR = (2m(OU + b)) / U(2m+1)
#
# If neither the quote nor base of the currency pair is the same as the account currency
#
# Buy Position MR = (2m(b - UOH)) / (1 - 2m)UH
# Sell Position MR = (2m(b + UOH)) / (1 + 2m)UH
#
# Where :
#
# MR = Margin Closeout rate (approx.)
# m = Margin Ratio
# U = Units Held
# O = Opening Rate of position
# b = Account Balance
# H = Quote Home rate (X/USD)
#
# Example for typical AUD/USD margin closeout with a 'BUY' position:
# m = 30 (30:1 Margin ratio)
# U = 200,000
# O = 0.55938
# b = 5700.02
#
# We will use the following formula : MR = (2m(OU - b)) / U(2m-1)
#
# MR = (2 * (30) * ((0.55938 * 200000) - 5700.02)) / (200000 * (2 * (30) - 1))
# MR = (60 * (111876 - 5700.02)) / (200000 * 59)
# MR = (60 * 106175.98) / (11800000)
# MR = 6370558.8 / 11800000
# MR = 0.53987


# Unit calculator
# This calculation uses the following formula:
# Margin Available * (margin ratio) / ({BASE}/{HOME Currency} Exchange Rate)
# For example, suppose:
# Home Currency: USD
# Currency Pair: GBP/CHF
# Margin Available: 100
# Margin Ratio : 20:1
# Base / Home Currency: GBP/USD = 1.584
# Then,
# Units = (100 * 20) / 1.584
# Units = 1262


# Profit/Loss calculator
# This calculation follows the following formula:
# (Closing Rate - Opening Rate) * (Closing {quote}/{home currency}) * Units
# For example, suppose:
#
# Home Currency: USD
# Currency Pair: GBP/CHF
# Base = GBP; Quote = CHF
# Quote / Home Currency = CHF/USD = 1.1025
# Opening Rate = 2.1443
# Closing Rate = 2.1452
# Units = 1000
#
# Then:
#
# Profit = (2.1452 - 2.1443) * (1.1025) * 1000
# Profit = 0.99225 USD

def profitLossRaw(open_rate, close_rate, units):
  """Calculate the profit/loss of a trade in the quoted currency.

    Parameters:
      open_rate   The rate at which the trade was opened (Decimal).
      close_rate  The rate at which the trade was closed (Decimal).
      units       The number of units traded (Decimal).

    Returns:
      The profit or loss induced by this trade in the quoted currency.
  """
  return (close_rate - open_rate) * units


def profitLossRawWithHome(open_rate, close_rate, quote_home_rate, units):
  """Calculate the profit/loss of a trade in the home currency.

    Parameters:
      open_rate        The rate at which the trade was opened (Decimal).
      close_rate       The rate at which the trade was closed (Decimal).
      quote_home_rate  The rate of the quoted currency to the home currency (Decimal).
      units            The number of units traded (Decimal).

    Returns:
      The profit or loss induced by this trade in the home currency.
  """
  return profitLossRaw(open_rate, close_rate, units) * quote_home_rate


class Trade:
  def __init__(self, server, currency):
    """XXX.

      Parameters:
        server    A server object to use for interaction with one of OANDA's servers.
        currency  String representing a currency pair. Note that the string is directly passed to
                  the OANDA API without any translation so it must correspond to a string as used by
                  this API.
    """
    self.__server = server
    self.__currency = currency


  def profitLoss(self):
    """XXX.

      Returns:
       XXX.
    """
    return None
