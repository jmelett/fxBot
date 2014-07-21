# currency.py

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

from price           import Price
from decimal         import Decimal
from logging         import debug
from datetime        import datetime, timedelta
from datetimeRfc3339 import parseDate


"""Dictionary for mapping granularities from user-friendly ones to OANDA specific ones."""
_granularities = {
  '5s':  'S5',
  '10s': 'S10',
  '15s': 'S15',
  '30s': 'S30',
  '1m':  'M1',
  '2m':  'M2',
  '3m':  'M3',
  '5m':  'M5',
  '10m': 'M10',
  '15m': 'M15',
  '30m': 'M30',
  '1h':  'H1',
  '2h':  'H2',
  '3h':  'H3',
  '4h':  'H4',
  '6h':  'H6',
  '8h':  'H8',
  '12h': 'H12',
  '1d':  'D',
  '1w':  'W',
  '1M':  'M',
}


def parsePrice(currency, price):
  """Parse a price value.

    Parameters:
      price  A dict object containing a 'time' value (string) and two prices, 'ask' and 'bid' (both
             strings).

    Returns:
      A dict object containing 'time' (datetime) and 'ask' and 'bid' (both Price objects).
  """
  return {'time': parseDate(price['time']),
          'ask':  Price(Decimal(price['ask']), currency.pip()),
          'bid':  Price(Decimal(price['bid']), currency.pip())}


class Currency:
  def __init__(self, server, currency):
    """Create new Currency object representing one currency being traded.

      Parameters:
        server    A server object to use for interaction with one of OANDA's servers.
        currency  String representing a currency pair. Note that the string is directly passed to
                  the OANDA API without any translation so it must correspond to a string as used by
                  this API.

      Notes:
        A currency does not necessarily have to be an actual currency pair -- any instrument
        tradeable on the market can be used.
    """
    self.__server = server
    self.__currency = currency
    # TODO: query actual value from server
    self.__pip = Decimal('0.001')


  def name(self):
    """Retrieve a name representing this currency.

      Returns:
        A string representing this currency.
    """
    return self.__currency


  def pip(self):
    """Retrieve the quantity of a pip in this currency.

      Returns:
        A Decimal with value 10^x, x in [...-10...0...+10...] representing a pip in this currency.
    """
    return self.__pip


  def currentPrices(self):
    """Retrieve the current bid and ask prices for this currency.

      Returns:
        A dict object containing the time ('time') as well as the associated ask and bid prices
        ('ask' and 'bid', respectively).
    """
    prices = self.__server.currentPrices(self.__currency)
    return parsePrice(self, prices)


  def history(self, granularity, count):
    """Retrieve past values of a currency.

       Retrieve a certain number of data points from the currency's past.

      Parameters:
        granularity  The granularity of the historic data to query.
        count        Amount of historic datapoints to retrieve.

      Returns:
        A list of dicts of the form {time: string, open: Decimal, close: Decimal} representing
        values at specific instances in time.

      Notes:
        All valid granularities can be found as the keys of the '_granularities' dict object.
    """
    granularity = _granularities[granularity]
    history = self.__server.history(self.__currency, granularity, count)

    # create our own list of dicts with our own set of indices and a reverse ordering where the newest
    # entries are at the lower indices
    values = []
    for value in history:
      values = [{'time': parseDate(value['time']),
                 'open': Price(Decimal(value['openMid']), self.__pip),
                 'close': Price(Decimal(value['closeMid']), self.__pip)}] + values
    return values
