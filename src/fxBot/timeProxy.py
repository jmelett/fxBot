# timeProxy.py

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


class TimeProxy:
  def __init__(self, server):
    """Create new TimeProxy object.

      Create a new TimeProxy object that inspects the reponses from a server to create an estimate
      of the server's current time by related the time encoded in the response to the system local
      time. Based on the delta the estimate can be created (actually, the proxy stores multiple
      deltas and calculates the estimate based on their average).

      Parameters:
        server  A Server object.
    """
    super().__init__(server)

    # the maximum number of time deltas we use
    self.__MAX_DELTA_COUNT = 5

    # lock to protect all time data
    self.__lock = Lock()
    self.__average_delta = None
    self.__time_deltas = []
    self.__delta_index = 0


  def currentPrices(self, *args, **kwargs):
    """Intercept a server's response to a request for the current prices."""
    prices = super().currentPrices(*args, **kwargs)
    self.feedTime(parseDate(prices['time']))
    return prices


  def history(self, *args, **kwargs):
    """Intercept a server's response to a history request."""
    history = super().history(*args, **kwargs)
    last = history[-1]

    # In case the last element is already complete we cannot say if it represents the server's
    # *current* time (and not just an aligned one) -- so do not use it.
    if not last['complete']:
      self.feedTime(parseDate(last['time']))

    return history


  def __updateAverageDelta(self):
    """Update the average delta between server time and local time.

      Notes:
        The object lock must be held during this call.
    """
    delta_sum = timedelta()

    for delta in self.__time_deltas:
      delta_sum += delta

    # update the average delta to reflect the new input data
    self.__average_delta = delta_sum / len(self.__time_deltas)


  def feedTime(self, time):
    """Update the proxy's estimate of the server's time with a current sample of the latter.

      Parameters:
        time  A datetime value representing the server's current time.

      Note:
        We assume that the time sample is from a recent request. More exactly, we relate the time to
        the system's *current* local time in order to calculate the delta.
    """
    with self.__lock:
      delta = datetime.now() - time

      if len(self.__time_deltas) < self.__MAX_DELTA_COUNT:
        self.__time_deltas.append(delta)
      else:
        self.__time_deltas[self.__delta_index] = delta
        self.__delta_index = (self.__delta_index + 1) % self.__MAX_DELTA_COUNT

      self.__updateAverageDelta()


  def estimatedTime(self):
    """Calculate an estimation of the server's current time.

      Returns:
        An estimation of the servers current time (datetime). None in case no estimation can be made
        due to a lack of intercepted responses containing the server's time.
    """
    with self.__lock:
      if self.__average_delta is None:
        return None

      return datetime.now() - self.__average_delta
