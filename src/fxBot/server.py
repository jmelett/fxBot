# server.py

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


class Server:
  def __init__(self, api):
    """Create new Server object representing a connection point with an OANDA server.

      Parameters:
        api  An object to use for interacting with OANDA's REST API.
    """
    self.__api = api


  def token(self):
    """Retrieve the access token used by this server object.

      Returns:
        A string representing the access token used by this object for communication with the OANDA
        server.
    """
    return self.__api.access_token


  def accounts(self):
    """Retrieve a list of all the user's accounts.

      Returns:
        A list of dict objects representing the user's accounts. It contains the following keys:
        'accountId', 'accountName', 'accountCurrency', and 'marginRate'.
      Examples:
        A possible return value might look like this:
        [{
          'accountId': 1815754,
          'accountName': 'Primary',
          'accountCurrency': 'EUR',
          'marginRate': 0.05,
        }]
    """
    return self.__api.get_accounts().get("accounts")


  def instruments(self, account_id, currencies):
    """Retrieve a list of available instruments for the account with the given ID.

      Parameters:
        account_id  The ID of the account for which to list the available instruments.
        currencies  (optional) Comma separated list of currencies to include in reply.

      Returns:
        A list of dict objects representing all instruments available on the given account or the
        ones listed, respectively. Each dict object contains the following keys:

      Examples:
        A possible return value might look like this:
        [{
          'pip': '0.01',
          'instrument': 'XAU_USD',
          'maxTradeUnits': 1000,
          'displayName': 'Gold'
        }]
    """
    return self.__api.get_instruments(account_id, instruments=currencies).get('instruments')


  def currentPrices(self, currency):
    """Retrieve the current bid and ask prices for a currency.

      Parameters:
        currency  String representing the currency for which to query the current prices.

      Returns:
        A dict object representing the current prices. It contains the following keys: 'instrument',
        'time', 'ask', 'bid', and 'status'.

      Examples:
        A possible return value might look like this:
        {
          'instrument': 'XAU_USD',
          'time': '2014-07-11T20:59:58.718193Z',
          'ask': 1339.211,
          'bid': 1336.661,
          'status': 'halted'
        }
    """
    return self.__api.get_prices(instruments=currency).get('prices')[0]


  def history(self, currency, granularity, count):
    """Query the server for a currency's historic data.

      Parameters:
        currency     Name of the currency for which to query the history.
        granularity  Granularity of the historic data to retrieve.
        count        Number of data points to retrieve.

      Returns:
        A list of dicts representing the various data points. Each dict has the following keys:
        'time', 'openMid', 'highMid', 'lowMid', 'closeMid', 'volume', and 'complete'.

      Examples:
        A possible return value might look like this:
        [{
          'time': '2014-07-02T00:00:00.000000Z',
          'openMid': 1.36803,
          'highMid': 1.368125,
          'lowMid': 1.364275,
          'closeMid': 1.365315,
          'volume': 28242,
          'complete': true
        }]
    """
    return self.__api.get_history(instrument=currency,
                                  granularity=granularity,
                                  #start=...,
                                  #end=datetime.now().isoformat('T') + 'Z',
                                  #includeFirst='false',
                                  candleFormat='midpoint',
                                  count=count).get('candles')


  def trades(self, account_id):
    """Query the server for the currently active trades.

      Parameters:
        account_id  The ID of the account for which to list the currently active trades.

      Returns:
        A list of dicts representing the currently open trades. Each dict has
        the following keys: 'id', 'time', 'instrument', 'units', 'side',
        'price', 'stopLoss', 'takeProfit', 'trailingStop', and 'trailingAmount'.

      Examples:
        A possible return value might look like this:
       [{
         'id': 612021234,
         'time': '2014-07-14T17:21:26.000000Z',
         'instrument': 'USB05Y_USD',
         'units': 80,
         'side': 'sell',
         'price': 119.895,
         'stopLoss': 120.15,
         'takeProfit': 119.4,
         'trailingStop': 0,
         'trailingAmount': 0
        }]

      TODO: handle pagination correctly
    """
    return self.__api.get_trades(account_id=account_id).get('trades')
