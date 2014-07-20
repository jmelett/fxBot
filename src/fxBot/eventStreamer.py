# eventStreamer.py

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

from threadedStreamer import ThreadedStreamer


class EventStreamer(ThreadedStreamer):
  def __init__(self, token, queue, *args, **kwargs):
    super().__init__(queue, access_token=token, *args, **kwargs)

    # overwrite the URL to use -- the Streamer class can only query rate streams, no event streams
    # TODO: find out which URL to use in case of a live account
    self.api_url = 'https://stream-fxpractice.oanda.com/v1/events'


  def on_success(self, data):
    """Handle received event data.

      Parameters:
        data  Data received from the server. May be a heartbeat message or an event such as a filled
              order.
    """
    self.queue.put(data)
