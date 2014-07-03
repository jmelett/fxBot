# fxBot.py

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

"""A trading bot for the Forex market using OANDA's REST API."""

from sys     import argv
from decimal import Decimal
from oandapy import API


def calculateEMA(values, count, avgKey, emaKey):
  """Calculate the Exponential Moving Average over a specifyable amount of values.

    Parameters:
      values  list of dicts
      count   number of elements for which to calculate the EMA
      avgKey  key into each of the dicts containing the average price
      emaKey  key into each of the dicts in which the EMA value is written

    Returns:
      A modified version of the given *values* list of dictionaries with each dictionary containing
      a new key (specified by *emaKey*) in which the calculated EMA is stored.

    Notes:
      Calculation is based on the formula:
        EMA_current = c * Price_current + (1-c) * EMA_previous
        where c = 2 / (n + 1)
        where n = # of periods
  """
  n = Decimal(count)
  c = Decimal(2) / (n + Decimal(1))

  # if 'count' is greater than len(values) we will see an exception
  # special treatment for the last element (the oldest)
  if count < len(values):
    # in case 'values' actually contains more values than specified by 'count' then grab the average
    # price of the previous element
    values[count - 1][emaKey] = values[count][avgKey]
  else:
    # if there are only 'count' elements in 'values' then take the average price of the last element
    values[count - 1][emaKey] = values[count - 1][avgKey]

  # loop over array from back to front -- front contains the most recent values which are based on
  # earlier ones
  for i in reversed(range(count - 1)):
    price_current = values[i][avgKey]
    ema_previous = values[i + 1][emaKey]

    values[i][emaKey] = c * price_current + (1 - c) * ema_previous

  return values


def calculateAvg(values, openKey, closeKey, avgKey):
  """Calculate the average price based on opening and closing prices.

    Parameters:
      values    A list of dictionaries containing values.
      openKey   The key into each of the dicts containing the opening price.
      closeKey  The key into each of the dicts containing the closing price.
      avgKey    The key into each of the dicts in which the average of the two values is written.

    Returns:
      A modified version of the given *values* list of dictionaries with each dictionary containing
      a new key (specified by *avgKey*) in which the calculated average is stored.
  """
  for value in values:
    value[avgKey] = (value[openKey] + value[closeKey]) / Decimal(2)

  return values


def main():
  if len(argv) != 2:
    print "No access token supplied."
    print "Usage: %s <access token>" % argv[0]
    exit(1)

  token = argv[1]
  oanda = API(environment="practice", access_token=token)


  prices = oanda.get_prices(instruments="EUR_USD").get("prices")
  history = oanda.get_history(instrument="EUR_USD",
                              granularity="H4",
                              #start=
                              #end=datetime.now().isoformat("T"),
                              #includeFirst=True,
                              candleFormat="midpoint",
                              count=20).get("candles")

  # create our own list of dicts with our own set of indices and a reverse ordering where the newest
  # entries are at the lower indices
  values = []
  for value in history:
    values = [{'time': value['time'],
               'open': Decimal(value['openMid']),
               'close': Decimal(value['closeMid'])}] + values

  calculateAvg(values, 'open', 'close', 'avg')
  calculateEMA(values, 10, 'avg', 'ema10')
  calculateEMA(values, 20, 'avg', 'ema20')

  print "EUR/USD:"
  print "current prices: ask=%s, bid=%s" % (prices[0]['ask'], prices[0]['bid'])
  print "historic data:"
  print "<time>                       <EMA 20>                          <EMA 10>"

  for value in values:
    print "%s: %s vs. %s" % (value['time'],
                             value['ema20'] if 'ema20' in value else '<nil>',
                             value['ema10'] if 'ema10' in value else '<nil>')


if __name__ == '__main__':
  main()
