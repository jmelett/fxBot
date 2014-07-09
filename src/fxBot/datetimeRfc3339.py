# datetimeRfc3339.py

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

from datetime import datetime


_format = '%Y-%m-%dT%H:%M:%S.%fZ'


def parseDate(string):
  """Parse a subset of times encoded as per RFC3339.

    Parameters:
      string  Date encoded as per RFC3339 to parse into a datetime object.

    Returns:
      A datetime object representing the given string.

    Notes:
      We rely only on Python's standard library. However, we do not support all features as
      specified in RFC3339. For instance, we always assume the timezone is UTC (which is encoded
      using a 'Z' at the end of the string).
  """
  return datetime.strptime(string, _format)


def formatDate(date):
  """Convert a datetime object to a string as per RFC3339.

    Parameters:
      date  The datetime object to convert.

    Returns:
      A string representing the given datetime object.

    Notes:
      We assume the date is given for UTC.
  """
  # note that replace() returns a new object
  assert date.replace(tzinfo = None) == date
  return datetime.strftime(date, _format)
