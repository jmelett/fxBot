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

from decimal    import Decimal
from oandapy    import API
from optparse   import OptionParser
from statistics import calculateAvg, calculateEMA


def main():
  usage = "Usage: %prog [options] <access token>"
  version = "%prog 0.1"

  parser = OptionParser(usage, version=version)
  parser.add_option("--list-accounts", dest="list_accounts", default=False,
                    action="store_true",
                    help="list all of a user's accounts")
  parser.add_option("--list-currencies", dest="list_currencies", default=False,
                    action="store_true",
                    help="list all available currencies")
  parser.add_option("-a", "--account-id", dest="account_id", default=None,
                    help="specify an account ID to use")

  (options, arguments) = parser.parse_args()

  if len(arguments) != 1:
    parser.error("invalid number of arguments")

  token = arguments[0]
  oanda = API(environment="practice", access_token=token)

  if options.list_accounts:
    idString = "id"
    nameString = "name"
    currencyString = "currency"
    idWidth = len(idString)
    nameWidth = len(nameString)

    accounts = oanda.get_accounts().get("accounts")

    for account in accounts:
      idWidth   = max(idWidth,   len(str(account['accountId'])))
      nameWidth = max(nameWidth, len(str(account['accountName'])))

    print "%s %s %s" % (idString.ljust(idWidth),
                        nameString.ljust(nameWidth),
                        currencyString)

    for account in accounts:
      print "%s %s %s" % (str(account['accountId']).ljust(idWidth),
                          str(account['accountName']).ljust(nameWidth),
                          str(account['accountCurrency']))
    exit(0)

  if options.list_currencies:
    if not options.account_id:
      parser.error("no account ID specified, use --account-id=<account ID>")

    nameString = "name"
    pipString = "pip"
    maxUnitsString = "maximum trade units"
    nameWidth = len(nameString)
    pipWidth = len(pipString)

    currencies = oanda.get_instruments(options.account_id).get('instruments')

    for currency in currencies:
      nameWidth = max(nameWidth, len(str(currency['displayName'])))
      pipWidth  = max(pipWidth,  len(str(currency['pip'])))

    print "%s %s %s" % (nameString.ljust(nameWidth),
                        pipString.ljust(pipWidth),
                        maxUnitsString)

    for currency in currencies:
      print "%s %s %s" % (str(currency['displayName']).ljust(nameWidth),
                          str(currency['pip']).ljust(pipWidth),
                          str(currency['maxTradeUnits']))
    exit(0)

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
