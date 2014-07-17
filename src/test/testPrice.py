# testPrice.py

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

from price           import Price
from currency        import Currency
from decimal         import Decimal
from datetime        import datetime
from datetimeRfc3339 import formatDate
from unittest        import TestCase, main


class TestCurrency(TestCase):
  def testString(self):
    price = Price(Decimal('12.123456'), Decimal('0.1'))
    self.assertEqual(str(price), '12.12')

    price = Price(Decimal('12.345678'), Decimal('0.1'))
    self.assertEqual(str(price), '12.35')


  def testAdd(self):
    price = Price(Decimal('12.345678'), Decimal('0.01'))
    price = price + Decimal('2')
    self.assertIsInstance(price, Price)
    self.assertEqual(str(price), '14.346')

    price = Price(Decimal('12.345678'), Decimal('0.01'))
    price = Decimal('2') + price
    self.assertIsInstance(price, Price)
    self.assertEqual(str(price), '14.346')


  def testSub(self):
    price = Price(Decimal('12.345678'), Decimal('1'))
    price = price - Decimal('5')
    self.assertIsInstance(price, Price)
    self.assertEqual(str(price), '7.3')

    price = Price(Decimal('12.345678'), Decimal('1'))
    price = Decimal('5') - price
    self.assertIsInstance(price, Price)
    self.assertEqual(str(price), '-7.3')


  def testMul(self):
    price = Price(Decimal('12.345678'), Decimal('0.0001'))
    price = price * Decimal('4.12345')
    self.assertIsInstance(price, Price)
    self.assertEqual(str(price), '50.90679')

    price = Price(Decimal('12.345678'), Decimal('0.0001'))
    price = Decimal('4.12345') * price
    self.assertIsInstance(price, Price)
    self.assertEqual(str(price), '50.90679')


  def testDiv(self):
    price = Price(Decimal('12.345678'), Decimal('0.00001'))
    price = price / Decimal('3.918')
    self.assertIsInstance(price, Price)
    self.assertEqual(str(price), '3.151015')

    price = Price(Decimal('12.345678'), Decimal('0.00001'))
    price = Decimal('3.918') / price
    self.assertIsInstance(price, Price)
    self.assertEqual(str(price), '0.317358')


if __name__ == '__main__':
  main()
