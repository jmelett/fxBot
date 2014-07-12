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

from decimal   import Decimal
from threading import Thread, Event
from logging   import info, warn
from Queue     import Queue


class Worker(Thread):
  def __init__(self, currencies):
    '''Create a new worker thread.

      Parameters:
        currencies  Dictionary indexed by currency names containing dictionaries containing currency
                    objects and associated strategies.
    '''

    # Please note that we have full control over the termination of the worker thread, i.e., we can
    # wake it up at any time by putting a dummy item in the queue, so there is no need to make this
    # thread a daemon thread like the stream threads.
    Thread.__init__(self)

    self.__currencies = currencies
    self.__queue = Queue()
    self.__destroy = Event()


  def handleTick(self, tick):
    '''Handle a tick received from the Oanda server.

      Parameters:
        tick  Dictionary containing timestamp string, time (datetime object), ask and bid prices
              (both Decimal objects).
    '''
    if tick['instrument'] in self.__currencies:
      pair = self.__currencies[tick['instrument']]
      pair['strategy'].onChange(pair['currency'], tick['time'],
                                tick['ask'], tick['bid'])
    else:
      warn("Received tick for unhandled currency: %s: %s ask=%s, bid=%s"
           % (tick['time'], tick['instrument'], tick['ask'], tick['bid']))


  def handleEvent(self, event):
    '''Handle an event received from the Oanda server.

      Parameters:
        event  Dictionary defining an event. The value of the 'type' should be investigated to get
        more details on the type of event.
    '''

    transaction = data['transaction']

    # transaction:
    # id                       Transaction ID
    # accountId                Account ID
    # time                     Time in a valid datetime format.
    # type                     Transaction type. Possible values: ORDER_FILLED, STOP_LOSS_FILLED,
    #                          TAKE_PROFIT_FILLED, TRAILING_STOP_FILLED, MARGIN_CLOSEOUT,
    #                          ORDER_CANCEL, MARGIN_CALL_ENTER, MARGIN_CALL_EXIT.
    # instrument               The name of the instrument.
    # side                     The direction of the action performed on the account, possible
    #                          values are: buy, sell.
    # units                    The amount of units involved.
    # price                    The execution or requested price.
    # lowerBound               The minimum execution price.
    # upperBound               The maximum execution price.
    # takeProfitPrice          The price of the take profit.
    # stopLossPrice            The price of the stop loss.
    # trailingStopLossDistance The distance of the trailing stop in pips, up to one decimal place.
    # pl                       The profit and loss value.
    # interest                 The interest accrued.
    # accountBalance           The balance on the account after the event.
    # tradeId                  ID of a trade that has been closed or opened
    # orderId                  ID of a filled order.
    # tradeOpened              This object is appended to the json response if a new trade has
    #                          been created. Trade related fields are: id, units.
    # tradeReduced             This object is appended to the json response if a trade has been
    #                          closed or reduced. Trade related fields are: id, units, pl,
    #                          interest.
    if transaction['type'] == "ORDER_FILLED":
      warn("%s: received event: %s" % (transaction['time'], transaction['type']))
    elif transaction['type'] == "STOP_LOSS_FILLED":
      warn("%s: received event: %s" % (transaction['time'], transaction['type']))
    elif transaction['type'] == "TAKE_PROFIT_FILLED":
      warn("%s: received event: %s" % (transaction['time'], transaction['type']))
    elif transaction['type'] == "TRAILING_STOP_FILLED":
      warn("%s: received event: %s" % (transaction['time'], transaction['type']))
    elif transaction['type'] == "MARGIN_CLOSEOUT":
      warn("%s: received event: %s" % (transaction['time'], transaction['type']))
    elif transaction['type'] == "ORDER_CANCEL":
      warn("%s: received event: %s" % (transaction['time'], transaction['type']))
    elif transaction['type'] == "MARGIN_CALL_ENTER":
      warn("%s: received event: %s" % (transaction['time'], transaction['type']))
    elif transaction['type'] == "MARGIN_CALL_EXIT":
      warn("%s: received event: %s" % (transaction['time'], transaction['type']))
    else:
      warn("%s: Unknown transaction event received: %s" % (transaction['time'],
                                                           transaction['type']))


  def run(self):
    '''Perform the actual work of processing newly incoming events.'''

    while True:
      data = self.__queue.get()

      if self.__destroy.is_set():
        break

      if 'transaction' in data:
        self.handleEvent(data['transaction'])
      # not sure if the API allows for heartbeat and transaction events at the same time (I think so),
      # but we don't care: if there is a transaction event we know something happened and we just
      # ignore the heartbeat (that's why we use elif)
      elif 'heartbeat' in data:
        heartbeat = data['heartbeat']
        info("%s: heartbeat" % heartbeat['time'])
      else:
        self.handleTick(data)


  def destroy(self):
    '''Destroy the worker thread.'''

    # Indicate to the thread that we want it to terminate and then insert something into the queue
    # to make it wake up unconditionally.
    self.__destroy.set()
    self.__queue.put([])


  def queue(self):
    '''Retrieve the queue on which this worker opperates.

      Returns:
        A queue object on which this thread waits for new work to be processed.
    '''
    return self.__queue
