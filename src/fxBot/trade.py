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
