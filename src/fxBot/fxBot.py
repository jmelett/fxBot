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

from signal   import signal, pause, SIGINT, SIGTERM
from logging  import basicConfig, addLevelName, WARNING
from optparse import OptionParser
from program  import Program
from oandapy  import API


_program = None
_terminate = False


def _onTerminate(signum, frame):
  """Handle the SIGINT and SIGTERM signals.

    Parameters:
      signum  Unused.
      frame   Unused.
  """
  global _program
  global _terminate

  _terminate = True

  if _program:
    _program.destroy()
    _program = None

  # Functions from the logging module may use a locking implementation that is not reentrant, so
  # using them from an asynchronous context such as a signal handler should be avoided, i.e., no
  # logging here.
  exit(0)


def main():
  """The main function parses the program arguments and reacts on them."""
  global _program
  global _terminate

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
  parser.add_option("-c", "--currencies", dest="currencies", default=None,
                    help="comma separated list of currencies to work with")
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
  # we redefine the names of the log levels that are printed
  addLevelName(10, "[DD]")
  addLevelName(20, "[II]")
  addLevelName(30, "[WW]")
  addLevelName(40, "[EE]")
  addLevelName(50, "[XX]")

  basicConfig(level=max(10, WARNING - options.verbosity * 10),
              format='%(asctime)s %(levelname)s %(message)s')

  # register our custom signal handler for SIGINT to tear down our objects correctly
  signal(SIGINT,  _onTerminate)
  signal(SIGTERM, _onTerminate)

  _program = Program(API(environment="practice", access_token=arguments[0]))

  if options.list_accounts:
    _program.listAccounts();
    exit(0)

  # all remaining paths require an account ID to be passed in
  if not options.account_id:
    parser.error("no account ID specified, use --account-id=<account ID>")

  if options.list_currencies:
    # note that the currencies parameters is optional, so it is okay if the user did not specify any
    # currencies
    _program.listCurrencies(options.account_id, options.currencies);
    exit(0)

  if not options.currencies:
    parser.error("no currencies specified, use --currencies=<C1,C2,...,Cn>")

  _program.start(options.account_id, options.currencies)

  # We must not exit here until we know that all threads are either torn down or are daemons anyway
  # (in which case they are forcefully shutdown when the program terminates). If we exit, nobody is
  # able to handle signals anymore and we are screwed.
  # So we block waiting for signals. Note that we should not hit a KeyboardInterrupt exception here
  # since we replaced the signal handler.
  while not _terminate:
    pause()


if __name__ == '__main__':
  main()
