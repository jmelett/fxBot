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

from optparse import OptionParser
from program  import Program


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
  program = Program(token)

  if options.list_accounts:
    program.listAccounts();
    exit(0)

  if options.list_currencies:
    if not options.account_id:
      parser.error("no account ID specified, use --account-id=<account ID>")

    program.listCurrencies(options.account_id);
    exit(0)

  program.run()


if __name__ == '__main__':
  main()
