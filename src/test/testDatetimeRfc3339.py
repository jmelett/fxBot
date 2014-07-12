# testDatetimeRfc3339.py

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

from datetime        import datetime
from datetimeRfc3339 import parseDate, formatDate
from unittest        import TestCase, main


class TestFxBot(TestCase):
  def testParse(self):
    """Test parsing of a couple of dates."""
    self.assertEqual(parseDate("2014-07-09T00:00:00.000000Z"), datetime(2014, 7, 9, 0, 0, 0, 0))
    self.assertEqual(parseDate("2014-07-09T01:00:00.000000Z"), datetime(2014, 7, 9, 1, 0, 0, 0))
    self.assertEqual(parseDate("2014-07-09T12:00:00.000000Z"), datetime(2014, 7, 9, 12, 0, 0, 0))
    self.assertEqual(parseDate("2014-07-09T12:00:00.000001Z"), datetime(2014, 7, 9, 12, 0, 0, 1))
    self.assertEqual(parseDate("2014-07-09T19:02:50.000082Z"), datetime(2014, 7, 9, 19, 2, 50, 82))


  def testFormat(self):
    self.assertEqual("2014-07-09T00:00:00.000000Z", formatDate(datetime(2014, 7, 9, 0, 0, 0, 0)))
    self.assertEqual("2014-07-09T01:00:00.000000Z", formatDate(datetime(2014, 7, 9, 1, 0, 0, 0)))
    self.assertEqual("2014-07-09T12:00:00.000000Z", formatDate(datetime(2014, 7, 9, 12, 0, 0, 0)))
    self.assertEqual("2014-07-09T12:00:00.000001Z", formatDate(datetime(2014, 7, 9, 12, 0, 0, 1)))
    self.assertEqual("2014-07-09T19:02:50.000082Z", formatDate(datetime(2014, 7, 9, 19, 2, 50, 82)))

if __name__ == '__main__':
  main()
