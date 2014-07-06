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

from decimal import Decimal


"""Dictionary for mapping granularities from user-friendly ones to OANDA specific ones."""
_granularities = {
  '5s':  'S5',  # 5 seconds
  '10s': 'S10', # 10 seconds
  '15s': 'S15', # 15 seconds
  '30s': 'S30', # 30 seconds
  '1m':  'M1',  # 1 minute
  # Top of the hour alignment
  '2m':  'M2',  # 2 minutes
  '3m':  'M3',  # 3 minutes
  '5m':  'M5',  # 5 minutes
  '10m': 'M10', # 10 minutes
  '15m': 'M15', # 15 minutes
  '30m': 'M30', # 30 minutes
  '1h':  'H1',  # 1 hour
  # Start of day alignment (17:00, Timezone/New York)
  '2h':  'H2',  # 2 hours
  '3h':  'H3',  # 3 hours
  '4h':  'H4',  # 4 hours
  '6h':  'H6',  # 6 hours
  '8h':  'H8',  # 8 hours
  '12h': 'H12', # 12 hours
  '1d':  'D',   # 1 Day
  # Start of week alignment (Saturday)
  '1w':  'W',   # 1 Week
  # Start of month alignment (First day of the month)
  '1M':  'M',   # 1 Month
}


class Currency:
  def __init__(self, api, currency):
    """Create new Currency object representing one currency being traded.

      Parameters:
        api       The API object to use for interaction with a server.
        currency  String representing a currency pair. Note that the string is directly passed to
                  the OANDA API without any translation so it must correspond to a string as used by
                  this API.

      Notes:
        A currency does not necessarily have to be an actual currency pair -- any instrument
        tradeable on the market can be used.

      TODO: we need a translation layer here: we want to pass in currencies as they are displayed
            but for the Oanda API we need the correct identifier
    """
    self.__api = api
    self.__currency = currency


  def name(self):
    """Retrieve a name representing this currency.

      Returns:
        A string representing this currency.
    """
    return self.__currency


  def currentPrices(self):
    """Retrieve the current bid and ask prices for this currency.

      Returns:
        A tuple (bid,ask) of Decimals representing the bid and ask prices.
    """
    prices = self.__api.get_prices(instruments=self.__currency).get("prices")
    return (Decimal(prices[0]['bid']), Decimal(prices[0]['ask']))


  def history(self, granularity, count):
    """Retrieve past values of a currency.

      Parameters:
        granularity  The granularity of the historic data to query.
        count        Amount of historic datapoints to retrieve.

      Returns:
        A list of dicts of the form {time: string, open: Decimal, close: Decimal} representing
        values at specific instances in time.

      Notes:
        All valid granularities can be found as the keys of the '_granularities' dict object.
    """
    if not granularity in _granularities:
      raise KeyError("Invalid granularity specified")

    granularity = _granularities[granularity]
    history = self.__api.get_history(instrument=self.__currency,
                                     granularity=granularity,
                                     #start=...,
                                     #end=datetime.now().isoformat("T") + "Z",
                                     #includeFirst="false",
                                     candleFormat="midpoint",
                                     count=count).get("candles")

    # create our own list of dicts with our own set of indices and a reverse ordering where the newest
    # entries are at the lower indices
    values = []
    for value in history:
      values = [{'time': value['time'],
                 'open': Decimal(value['openMid']),
                 'close': Decimal(value['closeMid'])}] + values

    return values
