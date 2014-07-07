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

from oandapy       import API
from currency      import Currency
from worker        import Worker
from eventStreamer import EventStreamer
from rateStreamer  import RateStreamer
from statistics    import calculateAvg, calculateEMA


class Program:
  def __init__(self, token):
    """Create new Program object using the given access token.

      Parameters:
        token  An access token to use for interacting with OANDA's REST API.
    """
    self.__api = API(environment="practice", access_token=token)
    self.__worker = Worker()
    self.__eventStreamer = EventStreamer(token, self.__worker.queue())
    self.__rateStreamer = RateStreamer(token, self.__worker.queue())


  def destroy(self):
    '''Destroy the program.'''
    self.__worker.destroy()
    self.__rateStreamer.disconnect()
    self.__eventStreamer.disconnect()


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
        # we assume that if a key is not present nothing will be printed
        if keys[i]['key'] in dictionary:
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

    print("%s %s %s" % (idString.ljust(widths[0]),
                        nameString.ljust(widths[1]),
                        currencyString))

    for account in accounts:
      print("%s %s %s" % (str(account['accountId']).ljust(widths[0]),
                          str(account['accountName']).ljust(widths[1]),
                          str(account['accountCurrency'])))


  def listCurrencies(self, account_id):
    """Print a list of all available currencies for the account with the given ID.

      Parameters:
        account_id  The ID of the account for which to list the available currencies.
    """
    nameString = "name"
    instrumentString = "instrument"
    pipString = "pip"
    maxUnitsString = "maximum trade units"

    currencies = self.__api.get_instruments(account_id).get('instruments')
    widths = self.__queryWidths(currencies, {'title': nameString, 'key': 'displayName'},
                                            {'title': instrumentString, 'key': 'instrument'},
                                            {'title': pipString,  'key': 'pip'})

    print("%s %s %s %s" % (nameString.ljust(widths[0]),
                           instrumentString.ljust(widths[1]),
                           pipString.ljust(widths[2]),
                           maxUnitsString))

    for currency in currencies:
      print("%s %s %s %s" % (str(currency['displayName']).ljust(widths[0]),
                             str(currency['instrument']).ljust(widths[1]),
                             str(currency['pip']).ljust(widths[2]),
                             str(currency['maxTradeUnits'])))


  def start(self, account_id):
    """Start the program.

      An invocation of this method causes the object to create the necessary infrastructure to
      subscribe for events and react on them.

      Note:
        Python has a very limited signal handling mechanism in that only the main thread can receive
        signals. In addition, it will receive/dispatch them only if it is actually running and not
        blocked in a system call. Since we use blocking primitives basically everywhere (the
        streamer uses them and so does the worker), we cannot perform any of this work synchronously
        here and risk to block. Instead, we create new threads for all tasks and return.
    """
    timeString = "time"
    ema20String = "EMA(20)"
    ema10String = "EMA(10)"

    currency = Currency(self.__api, "EUR_USD")
    history = currency.history('1h', 30)

    calculateAvg(history, 'open', 'close', 'avg')
    calculateEMA(history, 10, 'avg', 'ema10')
    calculateEMA(history, 20, 'avg', 'ema20')

    widths = self.__queryWidths(history, {'title': timeString,  'key': 'time'},
                                         {'title': ema20String, 'key': 'ema20'})

    print("EUR/USD:")
    print("current prices: bid=%s, ask=%s" % currency.currentPrices())
    print("historic data:")

    print("%s %s %s" % (timeString.ljust(widths[0]),
                        ema20String.ljust(widths[1]),
                        ema10String))

    for value in history:
      print("%s %s %s" % (str(value['time']).ljust(widths[0]),
                          str(value['ema20']).ljust(widths[1])
                            if 'ema20' in value
                            else '<nil>'.ljust(widths[1]),
                          str(value['ema10'])
                            if 'ema10' in value
                            else '<nil>'))

    # now start up all our threads
    self.__worker.start()
    self.__eventStreamer.start(accountId=account_id, ignore_heartbeat=False)
    self.__rateStreamer.start(accountId=account_id, instruments="EUR_USD")

    # We are done, we exit here -- the worker thread as well as the streamer threads will continue
    # running. Note that this is only due to f*cked up Python signal handling.
