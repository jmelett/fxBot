# program.py

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

from decimal    import Decimal
from oandapy    import API
from statistics import calculateAvg, calculateEMA


class Program:
  def __init__(self, token):
    """Create new Program object using the given access token.

      Parameters:
        token  An access token to use for interacting with OANDA's REST API.
    """
    self.__api = API(environment="practice", access_token=token)


  def __queryWidths(self, dictionaries, *keys):
    """Calculate the width of columns to represent various values.

      This method can be used to query the expected column width for a given set of values to be
      represented in it.

      Parameters:
        dictionaries  A list of dictionaries.
        keys          A list of dicts used to index into 'dictionaries'. Aach dictionary has to
                      contain two key-value pairs: The value of 'title' directly represents the
                      title of the column.
                      The value of 'key' is used to index into each dict of the dictionaries
                      argument to retrieve values to put into the column.

      Returns:
        A list of widths each being the maximum width of all the values retrieved when using all the
        given keys on each of the dictionaries.
    """
    widths = [len(key['title']) for key in keys]

    for dictionary in dictionaries:
      for i in range(len(keys)):
        widths[i] = max(widths[i], len(str(dictionary[keys[i]['key']])))

    return widths


  def listAccounts(self):
    """List all available accounts."""
    idString = "id"
    nameString = "name"
    currencyString = "currency"

    accounts = self.__api.get_accounts().get("accounts")
    widths = self.__queryWidths(accounts, {'title': idString,   'key': 'accountId'},
                                          {'title': nameString, 'key': 'accountName'})

    print "%s %s %s" % (idString.ljust(widths[0]),
                        nameString.ljust(widths[1]),
                        currencyString)

    for account in accounts:
      print "%s %s %s" % (str(account['accountId']).ljust(widths[0]),
                          str(account['accountName']).ljust(widths[1]),
                          str(account['accountCurrency']))


  def listCurrencies(self, account_id):
    """Print a list of all available currencies for the account with the given ID.

      Parameters:
        account_id  The ID of the account for which to list the available currencies.
    """
    nameString = "name"
    pipString = "pip"
    maxUnitsString = "maximum trade units"

    currencies = self.__api.get_instruments(account_id).get('instruments')
    widths = self.__queryWidths(currencies, {'title': nameString, 'key': 'displayName'},
                                            {'title': pipString,  'key': 'pip'})

    print "%s %s %s" % (nameString.ljust(widths[0]),
                        pipString.ljust(widths[1]),
                        maxUnitsString)

    for currency in currencies:
      print "%s %s %s" % (str(currency['displayName']).ljust(widths[0]),
                          str(currency['pip']).ljust(widths[1]),
                          str(currency['maxTradeUnits']))


  def run(self):
    prices = self.__api.get_prices(instruments="EUR_USD").get("prices")
    history = self.__api.get_history(instrument="EUR_USD",
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
