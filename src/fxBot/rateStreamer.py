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

from threadedStreamer import ThreadedStreamer


class RateStreamer(ThreadedStreamer):
  def __init__(self, token, queue, *args, **kwargs):
    super().__init__(queue, access_token=token, *args, **kwargs)


  def on_success(self, data):
    """Handle received 'tick' data.

      Parameters:
        data  Data received from the server. Represented as dict object containing 'instrument'
              string describing the currency, a 'time' string, an 'ask' price, and a 'bid' price.
    """
    self.queue.put(data)
