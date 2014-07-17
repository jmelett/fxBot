# tryRun.py

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

from os        import kill, getpid
from signal    import SIGTERM
from traceback import print_exc


def tryRun(function):
  """Dectorator used for catching any thrown exceptions and terminating the program.

    Parameters:
      function  The function the decorate.

    Returns:
      A decorating function handling all thrown exceptions raised by the given function.
  """
  def catch(*args, **kwargs):
    try:
      function(*args, **kwargs)
    except BaseException as exception:
      # print a stack trace and then signal the main thread to terminate gracefully (it should have
      # a signal handler for SIGTERM installed)
      print_exc()
      kill(getpid(), SIGTERM)

  return catch
