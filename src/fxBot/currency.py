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
  # Top of the minute alignment.
  '5s':  {'string': 'S5',  'time': timedelta(seconds=5)},
  '10s': {'string': 'S10', 'time': timedelta(seconds=10)},
  '15s': {'string': 'S15', 'time': timedelta(seconds=15)},
  '30s': {'string': 'S30', 'time': timedelta(seconds=30)},
  '1m':  {'string': 'M1',  'time': timedelta(minutes=1)},
  # Top of the hour alignment.
  '2m':  {'string': 'M2',  'time': timedelta(minutes=2)},
  '3m':  {'string': 'M3',  'time': timedelta(minutes=3)},
  '5m':  {'string': 'M5',  'time': timedelta(minutes=5)},
  '10m': {'string': 'M10', 'time': timedelta(minutes=10)},
  '15m': {'string': 'M15', 'time': timedelta(minutes=15)},
  '30m': {'string': 'M30', 'time': timedelta(minutes=30)},
  '1h':  {'string': 'H1',  'time': timedelta(hours=1)},
  # Start of day alignment (17:00, Timezone/New York).
  '2h':  {'string': 'H2',  'time': timedelta(hours=2)},
  '3h':  {'string': 'H3',  'time': timedelta(hours=3)},
  '4h':  {'string': 'H4',  'time': timedelta(hours=4)},
  '6h':  {'string': 'H6',  'time': timedelta(hours=6)},
  '8h':  {'string': 'H8',  'time': timedelta(hours=8)},
  '12h': {'string': 'H12', 'time': timedelta(hours=12)},
  '1d':  {'string': 'D',   'time': timedelta(hours=24)},
  # Start of week alignment (Saturday).
  # TODO: check if one week really is exactly one week in their sense and that we do not have to
  #       have additional logic for realignment etc.
  '1w':  {'string': 'W',   'time': timedelta(weeks=1)},
  # Start of month alignment (First day of the month).
  # TODO: check if four weeks really are a month in their sense
  '1M':  {'string': 'M',   'time': timedelta(weeks=4)},
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
    # dict indexed by the granularity we are looking for
    # {
    #   granularity:
    #   {
    #     'lastUpdate': datetime,
    #     'data': [{'time': datetime, 'open': Decimal, 'close': Decimal }]
    #   }
    # }
    self.__historyData = {}


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

       Retrieve a certain number of data points from the currency's past. This method employs
       a caching approach of data previously received from the server to avoid issuing too many
       requests to the server.

      Parameters:
        granularity  The granularity of the historic data to query.
        count        Amount of historic datapoints to retrieve.

      Returns:
        A list of dicts of the form {time: string, open: Decimal, close: Decimal} representing
        values at specific instances in time.

      Notes:
        All valid granularities can be found as the keys of the '_granularities' dict object.

      TODO: The caching approach still suffers from one problem: there is a potentially large gap
            between our system's current time and the server time. The data we receive is aligned
            based on the server's time. Now because of the time difference it is possible that we
            return data from our cache although there is already more recent data available on the
            server.
            To solve this issue we need to relate the server's time to our's. But there we have the
            problem that we do not reliably know the server's time (since that data is already
            aligned and we do not necessarily receive data for the "current" non-aligned time). One
            possible solution is to inspect all data from the server and update our view of the
            server's current time from that timestamp. Especially the eventStreamer's heartbeat
            might provide a reliable source even over the weekend or when markets are closed.
    """
    if not granularity in _granularities:
      raise KeyError("Invalid granularity specified")

    granularityString = _granularities[granularity]['string']
    granularityDelta  = _granularities[granularity]['time']

    # check if there is any data for the given granularity
    if granularityString in self.__historyData:
      data = self.__historyData[granularityString]

      # check if we got data from a last query that should still be current
      if datetime.now() - data['lastUpdate'] < granularityDelta:
        # check if that data contains enough timestamps
        if len(data['data']) >= count:
          debug("currency: cache-hit (currency=%s, granularity=%s)"
                  % (self.name(), granularity))
          return data['data'][0:count]

    # there is no or to few history data in our cache, get the history from the server
    history = self.__server.history(self.__currency, granularityString, count)

    # create our own list of dicts with our own set of indices and a reverse ordering where the newest
    # entries are at the lower indices
    values = []
    for value in history:
      values = [{'time': parseDate(value['time']),
                 'open': Price(Decimal(value['openMid']), self.__pip),
                 'close': Price(Decimal(value['closeMid']), self.__pip)}] + values

    # note that we could do much more effort to build the history incrementally by comparing
    # timestamps etc., but in the end this simple case just replacing all the stale data with all
    # the new data probably covers all relevant cases we are interested in
    self.__historyData[granularityString] = {'lastUpdate': datetime.now(), 'data': values}
    debug("currency: cache-miss (currency=%s, granularity=%s, count=%s)"
            % (self.name(), granularity, count))
    return values
