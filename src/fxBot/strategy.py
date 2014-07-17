# strategy.py

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

from logging import warn


class Strategy:
  def onChange(self, currency, time, ask, bid):
    """Handle a change in the currency's market value.

      Parameters:
        currency  The currency currently of interest.
        time      Time value when the change occurred, represented as datetime object.
        ask       Latest ask price for the given currency (Price).
        bid       Latest bid price for the given currency (Price).
    """
    warn("onChange: %s ask=%s bid=%s" % (currency.name(), ask, bid))
