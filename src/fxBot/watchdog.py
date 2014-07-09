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

from threading       import Thread, Event
from multiprocessing import Pipe
from select          import poll, POLLIN
from logging         import info, warn


class Watchdog(Thread):
  def __init__(self, currencies, queue):
    '''Create a new watchdog thread.

      Parameters:
        currencies  List of currencies managed by this worker.
        queue       A queue to use for placing new prices.
    '''

    Thread.__init__(self)
    pipePoll, pipeSignal = Pipe()

    self.__queue = queue
    self.__currencies = currencies
    self.__pipePoll = pipePoll
    self.__pipeSignal = pipeSignal
    self.__poll = poll()
    self.__destroy = Event()
    self.__timeout = 10000


  def run(self):
    '''Perform the actual work of processing newly incoming events.'''
    # we want to wait for incoming data
    self.__poll.register(self.__pipePoll, POLLIN)

    while True:
      self.__poll.poll(self.__timeout)

      if self.__destroy.is_set():
        break

      for pair in self.__currencies.values():
        # TODO: check if a tick is required (because none has been received for a long time) and
        #       only send it if so
        currency = pair['currency']
        prices = currency.currentPrices()
        self.__queue.put({'instrument': currency.name(),
                          'time': prices['time'],
                          'ask': prices['ask'],
                          'bid': prices['bid']})


  def destroy(self):
    '''Destroy the watchdog thread.'''
    self.__destroy.set()
    self.__pipeSignal.send([])
    self.__poll.unregister(self.__pipePoll)
    self.__pipePoll.close()
    self.__pipeSignal.close()
