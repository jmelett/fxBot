# watchdog.py

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

from tryRun          import tryRun
from threading       import Thread, Event
from multiprocessing import Pipe
from select          import poll, POLLIN


class Watchdog(Thread):
  def __init__(self, currencies, queue, timeout):
    '''Create a new watchdog thread.

      Parameters:
        currencies  List of currencies managed by this worker.
        queue       A queue to use for placing new prices.
        timeout     A timeout value (in milliseconds) after which the watchdog will query new prices
                    for a currency and place them in the queue.
    '''

    super().__init__()
    pipePoll, pipeSignal = Pipe()

    self.__queue = queue
    self.__currencies = currencies
    self.__pipePoll = pipePoll
    self.__pipeSignal = pipeSignal
    self.__poll = poll()
    self.__registered = False
    self.__destroy = Event()
    self.__timeout = timeout


  @tryRun
  def run(self):
    '''Perform the actual work of processing newly incoming events.'''
    # we want to wait for incoming data
    self.__poll.register(self.__pipePoll, POLLIN)
    self.__registered = True

    while True:
      self.__poll.poll(self.__timeout)

      if self.__destroy.is_set():
        break

      for pair in self.__currencies.values():
        # TODO: check if a tick is required (because none has been received for a long time) and
        #       only send it if so
        currency = pair['currency']
        prices = currency.currentPrices()
        prices['instrument'] = currency.name()
        prices['parsed'] = True
        self.__queue.put(prices)


  def destroy(self):
    '''Destroy the watchdog thread.'''
    self.__destroy.set()
    self.__pipeSignal.send([])

    if self.__registered:
      self.__poll.unregister(self.__pipePoll)

    self.__pipePoll.close()
    self.__pipeSignal.close()
