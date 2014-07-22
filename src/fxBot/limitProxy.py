# limitProxy.py

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

from time    import sleep, time
from logging import debug


# According to OANDA documents we are allowed to have 4 conncetions to the server per second (with
# peaks of 5). We assume that the rate and events streams do not count here.
# TODO: need to verify this assumption
_REQUEST_COUNT = 4


class LimitProxy:
  def __init__(self, server):
    """Create new LimitProxy object.

      Create a new LimitProxy object that limits connections per second to a server.

      Parameters:
        server  A Server object.

      TODO: This class has the problem that it is not safe against extensions of the Server class:
            everytime a new method is added it has to be declared here too. We need to find a better
            way to work around that.
      TODO: We require synchronization here in case multiple threads access such an object
            concurrently.
    """
    super().__init__(server)
    # a list of datetimes when the last requests occurred
    self.__last_requests = [0.0] * _REQUEST_COUNT
    # index to the datetime of the request that was performed last
    self.__last_request = 0


  def limit(function):
    def postpone(self, *args, **kwargs):
      self.__last_request = (self.__last_request + 1) % len(self.__last_requests)
      last = self.__last_requests[self.__last_request]
      # time.clock() would likely be the preferred function (presumably less overhead) but it won't
      # work as intended in conjunction with a blocking call such as sleep
      delta = time() - last

      # we want to wait until the most distant request happened at least one second ago
      while delta < 1.0:
        debug("limitProxy: too many request, postponing")
        sleep(1.0 - delta)
        delta = time() - last

      self.__last_requests[self.__last_request] = time()

      # default to None, if this case hits we get an exception which is as intended
      super_function = getattr(super(), function.__name__, None)
      return super_function(*args, **kwargs)

    return postpone


  @limit
  def accounts(self, *args, **kwargs):
    pass

  @limit
  def instruments(self, *args, **kwargs):
    pass

  @limit
  def currentPrices(self, *args, **kwargs):
    pass

  @limit
  def history(self, *args, **kwargs):
    pass

  @limit
  def trades(self, *args, **kwargs):
    pass
