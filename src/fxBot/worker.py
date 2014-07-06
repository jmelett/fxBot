# worker.py

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

from threading import Thread, Event
from Queue     import Queue


class Worker(Thread):
  def __init__(self):
    '''Create a new worker thread.'''

    # Please note that we have full control over the termination of the worker thread, i.e., we can
    # wake it up at any time by putting a dummy item in the queue, so there is no need to make this
    # thread a daemon thread like the stream threads.
    Thread.__init__(self)

    self.__queue = Queue()
    self.__destroy = Event()


  def run(self):
    '''Perform the actual work of processing newly incoming events.'''

    while True:
      data = self.__queue.get()

      if self.__destroy.is_set():
        break

      # process the data item!


  def destroy(self):
    '''Destroy the worker thread.'''

    # Indicate to the thread that we want it to terminate and then insert something into the queue
    # to make it wake up unconditionally.
    self.__destroy.set()
    self.__queue.put([])


  def queue(self):
    '''Retrieve the queue on which this worker opperates.

      Returns:
        Queue object on which this thread waits for new work to be processed.
    '''
    return self.__queue
