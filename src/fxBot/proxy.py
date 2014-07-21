# proxy.py

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


def createProxyInstance(server, *hierarchy):
  """Create a proxy object wrapping the given server and including a hierarchy of classes.

    Parameters:
      server     A Server object that is to be wrapped.
      hierarchy  A tuple of proxy classes in the order they should handle requests to the server.

    Returns:
      A proxy object that can be used to replace the given Server object but that all proxies as
      specified in the given hierarchy.

    Notes:
      It is important to take care to stack proxies in the correct order. For instance, having a
      proxy that inspects responses from a server for the current time run before a caching proxy is
      a bad idea as this might cause the time proxy to interpret cached responses (with old
      timestamps) as current requests (which are assumed to reflect the current time).

      Also note that all proxy classes specified in 'hierarchy' have to be constructible using only
      a Server object.
  """
  return type('ProxyServer', hierarchy + (_Proxy,), {})(server)


class _Proxy:
  def __init__(self, server):
    """Create new Proxy object.

      A proxy object interacts with a Server object but inspects the requests and responses to
      gather information from them. All Proxy objects implement the same interface as Server and
      should be able to be exchanged with it.

      Parameters:
        server  A Server object to which to send the request in case no proxy completed it
                beforehand.

      Notes:
        Objects of this type are used only internally for forwarding requests. Clients simply only
        implement the functionality they require based on the interface of a server from scratch.
    """
    self.__server = server


  def token(self, *args, **kwargs):         return self.__server.token(*args, **kwargs)
  def accounts(self, *args, **kwargs):      return self.__server.accounts(*args, **kwargs)
  def instruments(self, *args, **kwargs):   return self.__server.instruments(*args, **kwargs)
  def currentPrices(self, *args, **kwargs): return self.__server.currentPrices(*args, **kwargs)
  def history(self, *args, **kwargs):       return self.__server.history(*args, **kwargs)
  def trades(self, *args, **kwargs):        return self.__server.trades(*args, **kwargs)
