# TestFxBot.py

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

from statistics import calculateEMA
from decimal    import Decimal
from unittest   import TestCase, main


class TestFxBot(TestCase):
  def setUp(self):
    self.values1 =                [ {'avg': Decimal(0.1)} ]
    self.values2 = self.values1 + [ {'avg': Decimal(0.3)} ]
    self.values3 = self.values2 + [ {'avg': Decimal(0.2)} ]
    self.values5 = self.values3 + [ {'avg': Decimal(0.4)},
                                    {'avg': Decimal(0.8)} ]


  def testCalculateEMA1(self):
    calculateEMA(self.values1, 1, 'avg', 'ema1')

    self.assertEqual(len(self.values1), 1)
    self.assertEqual(self.values1[0]['ema1'], Decimal(0.1))


  def testCalculateEMA1Throws(self):
    self.assertRaises(IndexError, calculateEMA, self.values1, 2, 'avg', 'ema1')
    self.assertEqual(len(self.values1), 1)


  def testCalculateEMA2(self):
    calculateEMA(self.values2, 2, 'avg', 'ema2')

    self.assertEqual(len(self.values2), 2)
    c = Decimal(2) / Decimal(3)

    ema1 = Decimal(0.3)
    self.assertEqual(self.values2[1]['ema2'], ema1)

    ema0 = c * Decimal(0.1) + (1 - c) * Decimal(0.3)
    self.assertEqual(self.values2[0]['ema2'], ema0)


  def testCalculateEMA3(self):
    calculateEMA(self.values3, 3, 'avg', 'ema2')

    self.assertEqual(len(self.values3), 3)
    c = Decimal(2) / Decimal(4)

    ema2 = Decimal(0.2)
    self.assertEqual(self.values3[2]['ema2'], ema2)

    ema1 = c * Decimal(0.3) + (1 - c) * ema2
    self.assertEqual(self.values3[1]['ema2'], ema1)

    ema0 = c * Decimal(0.1) + (1 - c) * ema1
    self.assertEqual(self.values3[0]['ema2'], ema0)


  def testCalculateEMA5(self):
    calculateEMA(self.values5, 5, 'avg', 'ema5')

    self.assertEqual(len(self.values5), 5)
    c = Decimal(2) / Decimal(6)

    ema4 = Decimal(0.8)
    self.assertEqual(self.values5[4]['ema5'], ema4)

    ema3 = c * Decimal(0.4) + (1 - c) * ema4
    self.assertEqual(self.values5[3]['ema5'], ema3)

    ema2 = c * Decimal(0.2) + (1 - c) * ema3
    self.assertEqual(self.values5[2]['ema5'], ema2)

    ema1 = c * Decimal(0.3) + (1 - c) * ema2
    self.assertEqual(self.values5[1]['ema5'], ema1)

    ema0 = c * Decimal(0.1) + (1 - c) * ema1
    self.assertEqual(self.values5[0]['ema5'], ema0)


if __name__ == '__main__':
  main()
