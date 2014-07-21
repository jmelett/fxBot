# emaStrategy.py

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

from logging    import warning
from statistics import calculateAvg, calculateEMA
from strategy   import Strategy


class EmaStrategy(Strategy):
  def onChange(self, currency, time, ask, bid):
    """Handle a change in the currency's market value.

      Parameters:
        currency  The currency currently of interest.
        time      Time value when the change occurred, represented as datetime object.
        ask       Latest ask price for the given currency.
        bid       Latest bid price for the given currency.
    """
    #timeString = "time"
    #ema20String = "EMA(20)"
    #ema10String = "EMA(10)"

    #history = currency.history('1h', 30)

    #calculateAvg(history, 'open', 'close', 'avg')
    #calculateEMA(history, 10, 'avg', 'ema10')
    #calculateEMA(history, 20, 'avg', 'ema20')

    warning("onChange: %s ask=%s bid=%s" % (currency.name(), ask, bid))

    #widths = self.__queryWidths(history, {'title': timeString,  'key': 'time'},
    #                                     {'title': ema20String, 'key': 'ema20'})

    #print(currency.name())
    #prices = currency.currentPrices()
    #print("current prices: ask=%s, bid=%s" % (prices['ask'], prices['bid'])
    #print("historic data:")

    #print("%s %s %s" % (timeString.ljust(widths[0]),
    #                    ema20String.ljust(widths[1]),
    #                    ema10String))

    #for value in history:
    #  print("%s %s %s" % (str(value['time']).ljust(widths[0]),
    #                      str(value['ema20']).ljust(widths[1])
    #                        if 'ema20' in value
    #                        else '<nil>'.ljust(widths[1]),
    #                      str(value['ema10'])
    #                        if 'ema10' in value
    #                        else '<nil>'))
