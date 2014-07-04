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

"""A trading bot for the Forex market using Oanda's REST API."""

from sys     import argv
from decimal import Decimal
from oandapy import API


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
