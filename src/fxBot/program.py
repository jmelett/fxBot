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
from strategy      import Strategy
from worker        import Worker
from eventStreamer import EventStreamer
from rateStreamer  import RateStreamer


class Program:
  def __init__(self, token):
    """Create new Program object using the given access token.

      Parameters:
        token  An access token to use for interacting with OANDA's REST API.
    """
    self.__api = API(environment="practice", access_token=token)
    self.__worker = None
    self.__rateStreamer = None
    self.__eventStreamer = None


  def destroy(self):
    '''Destroy the program.'''
    if self.__worker:
      self.__worker.destroy()

    if self.__rateStreamer:
      self.__rateStreamer.disconnect()

    if self.__eventStreamer:
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


  def listCurrencies(self, account_id, currencies=None):
    """Print a list of all available currencies for the account with the given ID.

      Parameters:
        account_id  The ID of the account for which to list the available currencies.
        currencies  (optional) Comma separated list of currencies to list more information about.
    """
    nameString = "name"
    instrumentString = "instrument"
    pipString = "pip"
    maxUnitsString = "maximum trade units"

    instruments = self.__api.get_instruments(account_id, instruments=currencies).get('instruments')
    widths = self.__queryWidths(instruments, {'title': nameString, 'key': 'displayName'},
                                             {'title': instrumentString, 'key': 'instrument'},
                                             {'title': pipString,  'key': 'pip'})

    print("%s %s %s %s" % (nameString.ljust(widths[0]),
                           instrumentString.ljust(widths[1]),
                           pipString.ljust(widths[2]),
                           maxUnitsString))

    for instrument in instruments:
      print("%s %s %s %s" % (str(instrument['displayName']).ljust(widths[0]),
                             str(instrument['instrument']).ljust(widths[1]),
                             str(instrument['pip']).ljust(widths[2]),
                             str(instrument['maxTradeUnits'])))


  def start(self, account_id, currencies):
    """Start the program.

      An invocation of this method causes the object to create the necessary infrastructure to
      subscribe for events and react on them.

      Parameters:
        account_id  The ID of the account which to use for interaction with the OANDA servers.
        currencies  List of currencies managed by the program.

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
    currencyDict = {c: {'currency': Currency(self.__api, c),
                        'strategy': Strategy()} for c in currencySet}

    self.__worker = Worker(currencyDict)
    self.__eventStreamer = EventStreamer(self.__api.access_token, self.__worker.queue())
    self.__rateStreamer = RateStreamer(self.__api.access_token, self.__worker.queue())

    # now start up all our threads
    self.__worker.start()
    self.__eventStreamer.start(accountId=account_id, ignore_heartbeat=False)
    self.__rateStreamer.start(accountId=account_id, instruments=currencies)

    # We are done, we exit here -- the worker thread as well as the streamer threads will continue
    # running. Note that this is only due to f*cked up Python signal handling.
