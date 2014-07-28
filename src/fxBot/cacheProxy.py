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
from threading       import Lock
from logging         import debug, warning


_alignment_minute = {'microsecond': 0, 'second': 0}
_alignment_hour   = {'microsecond': 0, 'second': 0, 'minute': 0}
_alignment_day    = {'microsecond': 0, 'second': 0, 'minute': 0, 'hour': 0}

"""Dictionary for mapping granularities to timedeltas describing their length."""
_deltas = {
  # Top of the minute alignment.
  'S5':  {'delta': timedelta(seconds=5),  'alignment': _alignment_minute},
  'S10': {'delta': timedelta(seconds=10), 'alignment': _alignment_minute},
  'S15': {'delta': timedelta(seconds=15), 'alignment': _alignment_minute},
  'S30': {'delta': timedelta(seconds=30), 'alignment': _alignment_minute},
  'M1':  {'delta': timedelta(minutes=1),  'alignment': _alignment_minute},
  # Top of the hour alignment.
  'M2':  {'delta': timedelta(minutes=2),  'alignment': _alignment_hour},
  'M3':  {'delta': timedelta(minutes=3),  'alignment': _alignment_hour},
  'M5':  {'delta': timedelta(minutes=5),  'alignment': _alignment_hour},
  'M10': {'delta': timedelta(minutes=10), 'alignment': _alignment_hour},
  'M15': {'delta': timedelta(minutes=15), 'alignment': _alignment_hour},
  'M30': {'delta': timedelta(minutes=30), 'alignment': _alignment_hour},
  'H1':  {'delta': timedelta(hours=1),    'alignment': _alignment_hour},
  # Default alignment: Start of day alignment (17:00, Timezone/New York).
  # We change that to UTC by passing dailyAlignment='0' to the server.
  'H2':  {'delta': timedelta(hours=2),    'alignment': _alignment_day},
  'H3':  {'delta': timedelta(hours=3),    'alignment': _alignment_day},
  'H4':  {'delta': timedelta(hours=4),    'alignment': _alignment_day},
  'H6':  {'delta': timedelta(hours=6),    'alignment': _alignment_day},
  'H8':  {'delta': timedelta(hours=8),    'alignment': _alignment_day},
  'H12': {'delta': timedelta(hours=12),   'alignment': _alignment_day},
  'D':   {'delta': timedelta(hours=24),   'alignment': _alignment_day},
  # TODO: these next value are unsupported as of now
  # Default alignment: Start of week alignment (Saturday).
  # We change that to Monday by passing weeklyAlignment='Monday' to the server.
  # TODO: check if one week really is exactly one week in their sense and that we do not have to
  #       have additional logic for realignment etc.
  #'W':   {'delta': timedelta(weeks=1), 'alignment': timedelta(...)}
  # Start of month alignment (First day of the month).
  # TODO: check if four weeks really are a month in their sense
  #'M':   {'delta': timedelta(weeks=4), 'alignment': timedelta(...)}
}


class CacheProxy:
  def __init__(self, server):
    """Create new CacheProxy object.

      Create a new CacheProxy object that caches responses from a server.

      Parameters:
        server  A Server object.
    """
    super().__init__(server)
    # lock to protect our cached data
    self.__lock = Lock()
    # dict indexed by the granularity we are looking for
    # {
    #   currency: {
    #     granularity: {
    #       'lastUpdate': datetime,
    #       'data': [{'time': datetime, 'open': Decimal, 'close': Decimal }]
    #     }
    #   }
    # }
    self.__history_data = {}
    # if this proxy is used in conjunction with a TimeProxy we can retrieve an estimation of the
    # servers time using the 'estimatedTime' method -- here we try to query a reference to it
    self.__time_source = getattr(self, "estimatedTime", None)

    if not self.__time_source:
      warning("cacheProxy: no server time estimation possible")


  def __cacheLineStillValid(self, data, delta_data):
    """Check if a cache line is still valid.

      Parameters:
        data        The cache line data, i.e., a '__history_data' entry already indexed by currency
                    and granularity.
        delta_data  An entry of the '_deltas' dict.

      Returns:
        True in case the given cache line data is estimated to be still the most up to date data
        available, false if new data should be queried from the server.
    """
    now = datetime.now()
    delta = delta_data['delta']
    last_update = data['lastUpdate']

    # We have two approaches for checking whether a cached entry is still valid (i.e., holds the
    # most recent data):
    # 1) By simply comparing the timestamp of the last update with the current time. If the
    #    difference is greater than the granularity of the data, the server must have new data and
    #    we should query it. This approach works but it suffers from the problem that we might
    #    not always detect that the server has new data.
    #    Consider the following example:
    #      The last request was at 11:13 local time, which corresponds to 13:47 server time. At the
    #      current request, the local time is 11:30. Assuming a granularity of 1h we do no update
    #      because the next update is due only 12:13. However, the server's current time is 13:04,
    #      meaning it changed the hour. Now, because the server's data is hour aligned, if we send a
    #      new request to the server we should get a new data point in the history. So we should not
    #      return the cached data.
    # 2) In order to cope with this last problem, we use an estimation of the server's time to
    #    assess whether or not the *server* increased time above a granularity boundary.
    if self.__time_source and self.__time_source() is not None:
      # First we need to get a hold on the server's time, now and when the last request is
      # made. We can retrieve it by rearranging the following equation:
      # LT_now - LT_last = ST_now - ST_last
      # --> ST_last = ST_now - (LT_now - LT_last)
      local_time_now = now
      local_time_last = last_update
      server_time_now = self.__time_source()
      server_time_last = server_time_now - (local_time_now - local_time_last)

      # Now that we have the time we need to relate it to the same reference as the server
      # does. The server aligns the data based on the given granularity:
      # if 0s < granularity && granularity <= 1m -> one minute
      # if 1m < granularity && granularity <= 1h -> one hour
      # if 1h < granularity && granularity <= 1d -> one day (day starts at 0:00 UTC)
      # greater granularities are currently not supported
      server_time_now_aligned = server_time_now.replace(**delta_data['alignment'])
      server_time_last_aligned = server_time_last.replace(**delta_data['alignment'])

      # If the time advanced so far that the aligned time base changed then we defintely need to
      # query the server.
      if server_time_now_aligned > server_time_last_aligned:
        return False

      assert server_time_now_aligned == server_time_last_aligned

      # Otherwise we need to relate the actual times to the aligned one(s).
      d1 = server_time_last - server_time_last_aligned
      d2 = server_time_now - server_time_last_aligned

      # And if the difference between the two is still smaller than the 'granularity' then we still
      # have up-to-date data in our cache, otherwise we need to query the server for new data.
      return d2 - d1 < delta
    else:
      return now - last_update < delta


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
    """
    with self.__lock:
      if currency in self.__history_data:
        currency_data = self.__history_data[currency]

        # check if there is any data for the given granularity
        if granularity in currency_data:
          data = currency_data[granularity]
          delta = _deltas[granularity]
          still_valid = self.__cacheLineStillValid(data, delta)

          # check if we got data from a last query that should still be current
          if still_valid:
            # check if that data contains enough timestamps
            if len(data['data']) >= count:
              debug("cacheProxy: cache-hit (currency=%s, granularity=%s, count=%s)"
                      % (currency, granularity, count))
              return data['data'][0:count]
      else:
        self.__history_data[currency] = {}

    # there is no or to few history data in our cache, get the history from the server
    history = super().history(currency, granularity, count)
    cache_line = {'lastUpdate': datetime.now(), 'data': history}

    # We released the lock in between so we might actually overwrite data written when the lock was
    # released. We do not care because any entry that we put in is valid -- we have no preference.
    with self.__lock:
      # note that we could do much more effort to build the history incrementally by comparing
      # timestamps etc., but in the end this simple case just replacing all the stale data with all
      # the new data probably covers all relevant cases we are interested in
      self.__history_data[currency][granularity] = cache_line

    debug("cacheProxy: cache-miss (currency=%s, granularity=%s, count=%s)"
            % (currency, granularity, count))
    return history


  def invalidate(self):
    """Invalidate all cache contents."""
    with self.__lock:
      self.__history_data = {}

    warning("cacheProxy: cache invalidated")
