# rateStreamer.py

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

from logging          import info, warn, error
from threadedStreamer import ThreadedStreamer


class RateStreamer(ThreadedStreamer):
  def __init__(self, token, queue, *args, **kwargs):
    ThreadedStreamer.__init__(self, queue, access_token=token, *args, **kwargs)


  def on_success(self, data):
    if 'tick' in data:
      self.queue.put(data)
    elif 'heartbeat' in data:
      heartbeat = data['heartbeat']
      info("%s: rate heartbeat" % heartbeat['time'])
    else:
      warn("Unknown data received: %s", data)


  def on_error(self, data):
    # TODO: find out if a timestamp is delived here
    error("an error occurred: %s" % data)
    self.disconnect()
