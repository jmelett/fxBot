# price.py

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

from decimal import Decimal, ROUND_HALF_EVEN


class Price:
  def __init__(self, value, pip):
    """Create a new price object given a value and the quantity of a pip.

      Parameters:
        value  A price (Decimal).
        pip    Quantity of a pip (Decimal).
    """
    self.__value = Decimal(value)
    self.__pip = Decimal(pip)


  def __str__(self):
    """Get a string representation of the Price object."""
    # ROUND_HALF_EVEN is often referred to as Banker's Rounding and used in many financial
    # applications. Note that we always care for 1/10th of a pip.
    return str(self.__value.quantize(self.__pip * Decimal('0.1'), rounding=ROUND_HALF_EVEN))


  def __neg__(self):
    """Get the negated price.

      Returns:
        New Price object created by negating this Price object.
    """
    return Price(-self.__value, self.__pip)


  def __add__(self, value):
    """Add a value to the Price object.

      Parameters:
        value  Some value to add to the Price object.

      Returns:
        New Price object created by adding the given value to this Price object.
    """
    if type(value) not in (Price, Decimal):
      raise TypeError('unsupported operand type(s) for +: \'' +
                      type(self).__name__ + '\' and \'' +
                      type(value).__name__ + '\'')
    return Price(self.__value + value, self.__pip)


  def __radd__(self, value):
    """Add a value to the Price object.

      Parameters:
        value  Some value to add to the Price object.

      Returns:
        New Price object created by adding the given value to this Price object.
    """
    return self + value


  def __sub__(self, value):
    """Subtract a value from the Price object.

      Parameters:
        value  Some value to subtract from the Price object.

      Returns:
        New Price object created by subtracting the given value from this Price object.
    """
    if type(value) not in (Price, Decimal):
      raise TypeError('unsupported operand type(s) for -: \'' +
                      type(self).__name__ + '\' and \'' +
                      type(value).__name__ + '\'')
    return Price(self.__value - value, self.__pip)


  def __rsub__(self, value):
    """Subtract a value from the Price object.

      Parameters:
        value  Some value to subtract from the Price object.

      Returns:
        New Price object created by subtracting the given value from this Price object.
    """
    return -(self - value)


  def __mul__(self, value):
    """Multiply a value with the Price object.

      Parameters:
        value  Some value to multiply the Price object with.

      Returns:
        New Price object created by multiplying the given value with this Price object.
    """
    if type(value) not in (Price, Decimal):
      raise TypeError('unsupported operand type(s) for *: \'' +
                      type(self).__name__ + '\' and \'' +
                      type(value).__name__ + '\'')
    return Price(self.__value * value, self.__pip)


  def __rmul__(self, value):
    """Multiply a value with the Price object.

      Parameters:
        value  Some value to multiply the Price object with.

      Returns:
        New Price object created by multiplying the given value with this Price object.
    """
    return self * value


  def __div__(self, value):
    """Divide the Price object by a value.

      Parameters:
        value  Some value to divide the Price object by.

      Returns:
        New Price object created by dividing the Price object by the given value.
    """
    if type(value) not in (Price, Decimal):
      raise TypeError('unsupported operand type(s) for /: \'' +
                      type(self).__name__ + '\' and \'' +
                      type(value).__name__ + '\'')
    return Price(self.__value / value, self.__pip)


  def __rdiv__(self, value):
    """Divide the Price object by a value.

      Parameters:
        value  Some value to divide the Price object by.

      Returns:
        New Price object created by dividing the Price object by the given value.
    """
    return Price(value / self.__value, self.__pip)
