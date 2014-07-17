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

from currency      import Currency
from strategy      import Strategy
from worker        import Worker
from watchdog      import Watchdog
from eventStreamer import EventStreamer
from rateStreamer  import RateStreamer


class Program:
  def __init__(self, server):
    """Create new Program object using the given access token.

      Parameters:
        server  An object to use for interacting with an OANDA server.
    """
    self.__server = server
    self.__worker = None
    self.__watchdog = None
    self.__rateStreamer = None
    self.__eventStreamer = None


  def destroy(self):
    '''Destroy the program.'''
    self.__eventStreamer.disconnect() if self.__eventStreamer else None
    self.__rateStreamer.disconnect()  if self.__rateStreamer else None
    self.__watchdog.destroy()         if self.__watchdog else None
    self.__worker.destroy()           if self.__worker else None


  def __queryWidths(self, dictionaries, *keys):
    """Calculate the width of columns to represent various values.

      This method can be used to query the expected column width for a given set of values to be
      represented in it.

      Parameters:
        dictionaries  A list of dictionaries.
        keys          A list of keys to index into the given list of dictionaries to retrieve the
                      actual values to put into the column.

      Returns:
        A list of widths each being the maximum width of all the values retrieved when using all the
        given keys on each of the dictionaries.
    """
    widths = [0 for key in keys]

    for dictionary in dictionaries:
      for i in range(len(keys)):
        # we assume that if a key is not present nothing will be printed
        if keys[i] in dictionary:
          widths[i] = max(widths[i], len(str(dictionary[keys[i]])))

    return widths


  def listAccounts(self):
    """List all available accounts."""
    titles = [{'accountId': 'id', 'accountName': 'name', 'accountCurrency': 'currency'}]

    accounts = titles + self.__server.accounts()
    widths = self.__queryWidths(accounts, 'accountId', 'accountName', 'accountCurrency')

    for account in accounts:
      print("%s %s %s" % (str(account['accountId']).ljust(widths[0]),
                          str(account['accountName']).ljust(widths[1]),
                          str(account['accountCurrency']).ljust(widths[2])))


  def listCurrencies(self, account_id, currencies=None):
    """Print a list of all available currencies for the account with the given ID.

      Parameters:
        account_id  The ID of the account for which to list the available currencies.
        currencies  (optional) Comma separated list of currencies to list more information about.
    """
    titles = [{'displayName': 'name', 'instrument': 'instrument', 'pip': 'pip',
               'maxTradeUnits': 'maximum trade units'}]
    instruments = titles + self.__server.instruments(account_id, currencies)
    widths = self.__queryWidths(instruments, 'displayName', 'instrument', 'pip', 'maxTradeUnits')

    for instrument in instruments:
      print("%s %s %s %s" % (str(instrument['displayName']).ljust(widths[0]),
                             str(instrument['instrument']).ljust(widths[1]),
                             str(instrument['pip']).ljust(widths[2]),
                             str(instrument['maxTradeUnits']).ljust(widths[3])))


  def listTrades(self, account_id):
    """Print a list of all currently active trades.

      Parameters:
        account_id  The ID of the account for which to list the trades.
    """
    titles = [{'id': 'id', 'instrument': 'currency', 'units': 'units',
               'side': 'side', 'price': 'price', 'stopLoss': 'SL',
               'takeProfit': 'TP', 'trailingStop': 'TS'}]

    trades = titles + self.__server.trades(account_id)
    widths = self.__queryWidths(trades, 'id', 'instrument', 'units', 'side', 'price',
                                        'stopLoss', 'takeProfit', 'trailingStop')

    for trade in trades:
      print("%s %s %s %s %s %s %s %s" % (str(trade['id']).ljust(widths[0]),
                                         str(trade['instrument']).ljust(widths[1]),
                                         str(trade['units']).ljust(widths[2]),
                                         str(trade['side']).ljust(widths[3]),
                                         str(trade['price']).ljust(widths[4]),
                                         str(trade['stopLoss']).ljust(widths[5]),
                                         str(trade['takeProfit']).ljust(widths[6]),
                                         str(trade['trailingStop']).ljust(widths[7])))


  def start(self, account_id, currencies, timeout):
    """Start the program.

      An invocation of this method causes the object to create the necessary infrastructure to
      subscribe for events and react on them.

      Parameters:
        account_id  The ID of the account which to use for interaction with the OANDA servers.
        currencies  List of currencies managed by the program.
        timeout     A timeout value (in milliseconds) after which the watchdog will query new prices
                    for a currency and place them in the queue.

      Note:
        Python has a very limited signal handling mechanism in that only the main thread can receive
        signals. In addition, it will receive/dispatch them only if it is actually running and not
        blocked in a system call. Since we use blocking primitives basically everywhere (the
        streamer uses them and so does the worker), we cannot perform any of this work synchronously
        here and risk to block. Instead, we create new threads for all tasks and return.
    """
    # create a set of currency names we are interested in (removes potential duplicates)
    currencySet = set([c.strip() for c in currencies.split(',')])
    # for now we associate an empty Strategy with every currency
    currencyDict = {c: {'currency': Currency(self.__server, c),
                        'strategy': Strategy()} for c in currencySet}

    self.__worker = Worker(currencyDict)
    self.__watchdog = Watchdog(currencyDict, self.__worker.queue(), timeout)
    self.__rateStreamer = RateStreamer(self.__server.token(), self.__worker.queue())
    self.__eventStreamer = EventStreamer(self.__server.token(), self.__worker.queue())

    # now start up all our threads
    self.__worker.start()
    self.__watchdog.start()
    self.__rateStreamer.start(accountId=account_id, instruments=currencies)
    self.__eventStreamer.start(accountId=account_id, ignore_heartbeat=False)

    # We are done, we exit here -- the worker thread as well as the streamer threads will continue
    # running. Note that this is only due to f*cked up Python signal handling.
