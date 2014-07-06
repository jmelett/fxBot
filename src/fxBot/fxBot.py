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

from signal   import signal, SIGINT, SIGTERM
from logging  import basicConfig, WARNING
from optparse import OptionParser
from program  import Program


_program = None


def _onTerminate(signum, frame):
  """Handle the SIGINT and SIGTERM signals.

    Parameters:
      signum  Unused.
      frame   Unused.
  """
  if _program:
    _program.destroy()

  # functions from the logging module are not necessarily reentrant and may grab locks, so using
  # them from an asynchronous context such as a signal handler should be avoided
  exit(0)


def main():
  """The main function parses the program arguments and reacts on them."""
  global _program

  usage = "Usage: %prog [options] <access token>"
  version = "%prog 0.1"

  parser = OptionParser(usage, version=version)
  parser.add_option("--list-accounts", dest="list_accounts", default=False,
                    action="store_true", help="list all of a user's accounts")
  parser.add_option("--list-currencies", dest="list_currencies", default=False,
                    action="store_true", help="list all available currencies")
  parser.add_option("-a", "--account-id", dest="account_id", default=None,
                    help="specify an account ID to use")
  parser.add_option("-v", "--verbose", dest="verbosity", default=0,
                    action="count",
                    help="increase verbosity of output")

  (options, arguments) = parser.parse_args()

  if len(arguments) != 1:
    parser.error("invalid number of arguments")

  # numeric values of the logging levels:
  # CRITICAL  50
  # ERROR     40
  # WARNING   30
  # INFO      20
  # DEBUG     10
  # NOTSET    0
  basicConfig(level=max(10, WARNING - options.verbosity * 10))

  # register our custom signal handler for SIGINT to tear down our objects correctly
  signal(SIGINT,  _onTerminate)
  signal(SIGTERM, _onTerminate)

  _program = Program(token=arguments[0])

  if options.list_accounts:
    _program.listAccounts();
    exit(0)

  # all remaining paths require an account ID to be passed in
  if not options.account_id:
    parser.error("no account ID specified, use --account-id=<account ID>")

  if options.list_currencies:
    _program.listCurrencies(options.account_id);
    exit(0)

  _program.run(options.account_id)


if __name__ == '__main__':
  main()
