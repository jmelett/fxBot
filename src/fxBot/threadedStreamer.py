# threadedStreamer.py

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

from tryRun    import tryRun
from oandapy   import Streamer
from logging   import error
from threading import Thread


# TODO: think about making this function a classmethod of ThreadedStreamer
@tryRun
def _start(self, *args, **kwargs):
  Streamer.start(self, *args, **kwargs)


class StreamError(Exception):
  def __init__(self, data):
    """Create a new StreamError object.

      Parameters:
        data  Some object not clearly specified containing information related to an error that
              occurred.
    """
    self.__data = data


  def __str__(self):
    """Get a textual representation of the error.

      Returns:
        A textual representation of the error.
    """
    return str(self.__data)


class ThreadedStreamer(Streamer):
  def __init__(self, queue, *args, **kwargs):
    Streamer.__init__(self, *args, **kwargs)
    self.queue = queue


  def start(self, *args, **kwargs):
    self.__thread = Thread(target=_start, args=(self, ) + args, kwargs=kwargs)
    # We have the problem how to terminate the streamer threads, e.g., when a signal occurred. We
    # already call disconnect() on it which sets a flag to indicate to terminate the internal loop
    # to quit but we are still stuck in some system call. The only solution from what I can tell
    # (since we cannot forcefully terminate a thread nor adjust the OANDA API, nor hook into it to
    # use poll/select and a mechanism such as set_wakeup_fd) is to run the streamer threads as
    # daemons which means we do not wait for them to complete if the main thread exits.
    self.__thread.setDaemon(True)
    self.__thread.start()


  def on_success(self, data):
    """Handle received data.

      Parameters:
        data  Data received from the server. Format, type, and meaning differ among subclasses.
    """
    # derived classes may overwrite this method
    return


  def on_error(self, data):
    raise StreamError(data)
