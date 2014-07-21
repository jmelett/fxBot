# cacheProxy.py

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

from datetimeRfc3339 import parseDate
from datetime        import datetime, timedelta
from logging         import debug


"""Dictionary for mapping granularities to timedeltas describing their length."""
_deltas = {
  # Top of the minute alignment.
  'S5':  timedelta(seconds=5),
  'S10': timedelta(seconds=10),
  'S15': timedelta(seconds=15),
  'S30': timedelta(seconds=30),
  'M1':  timedelta(minutes=1),
  # Top of the hour alignment.
  'M2':  timedelta(minutes=2),
  'M3':  timedelta(minutes=3),
  'M5':  timedelta(minutes=5),
  'M10': timedelta(minutes=10),
  'M15': timedelta(minutes=15),
  'M30': timedelta(minutes=30),
  'H1':  timedelta(hours=1),
  # Start of day alignment (17:00, Timezone/New York).
  'H2':  timedelta(hours=2),
  'H3':  timedelta(hours=3),
  'H4':  timedelta(hours=4),
  'H6':  timedelta(hours=6),
  'H8':  timedelta(hours=8),
  'H12': timedelta(hours=12),
  'D':   timedelta(hours=24),
  # Start of week alignment (Saturday).
  # TODO: check if one week really is exactly one week in their sense and that we do not have to
  #       have additional logic for realignment etc.
  'W':   timedelta(weeks=1),
  # Start of month alignment (First day of the month).
  # TODO: check if four weeks really are a month in their sense
  'M':   timedelta(weeks=4),
}


class CacheProxy:
  def __init__(self, server):
    """Create new CacheProxy object.

      Create a new CacheProxy object that caches responses from a server.

      Parameters:
        server  A Server object.
    """
    super().__init__(server)
    # dict indexed by the granularity we are looking for
    # {
    #   currency: {
    #     granularity:
    #     {
    #       'lastUpdate': datetime,
    #       'data': [{'time': datetime, 'open': Decimal, 'close': Decimal }]
    #     }
    #   }
    # }
    self.__historyData = {}


  def history(self, currency, granularity, count):
    """Intercept a history request to a server.

       Retrieve a certain number of historic data points for a currency. This method employs a
       caching approach of data previously received from the server to avoid issuing too many
       requests to the server.

      Parameters:
        currency     Name of the currency for which to query the history.
        granularity  The granularity of the historic data to query.
        count        Number of data points to retrieve.

      Returns:
        A list of dicts representing the various data points. Each dict has the following keys:
        'time', 'openMid', 'highMid', 'lowMid', 'closeMid', 'volume', and 'complete'.

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
    # check if there is any data for the given granularity
    if currency in self.__historyData:
      currencyData = self.__historyData[currency]

      if granularity in currencyData:
        data = currencyData[granularity]
        delta = _deltas[granularity]

        # check if we got data from a last query that should still be current
        if datetime.now() - data['lastUpdate'] < delta:
          # check if that data contains enough timestamps
          if len(data['data']) >= count:
            debug("currency: cache-hit (currency=%s, granularity=%s, count=%s)"
                    % (currency, granularity, count))
            return data['data'][0:count]
    else:
      self.__historyData[currency] = {}

    # there is no or to few history data in our cache, get the history from the server
    history = super().history(currency, granularity, count)
    cache_line = {'lastUpdate': datetime.now(), 'data': history}

    # note that we could do much more effort to build the history incrementally by comparing
    # timestamps etc., but in the end this simple case just replacing all the stale data with all
    # the new data probably covers all relevant cases we are interested in
    self.__historyData[currency][granularity] = cache_line
    debug("cacheProxy: cache-miss (currency=%s, granularity=%s, count=%s)"
            % (currency, granularity, count))
    return history
