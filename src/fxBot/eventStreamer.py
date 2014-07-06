# eventStreamer.py

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

from logging import info, warn, error
from oandapy import Streamer


class EventStreamer(Streamer):
  def __init__(self, token, *args, **kwargs):
    Streamer.__init__(self, access_token=token, *args, **kwargs)

    # overwrite the URL to use -- the Streamer class can only query rate streams, no event streams
    # TODO: find out which URL to use in case of a live account
    self.api_url = 'https://stream-fxpractice.oanda.com/v1/events'


  def on_success(self, data):
    if 'transaction' in data:
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
    # not sure if the API allows for heartbeat and transaction events at the same time (I think so),
    # but we don't care: if there is a transaction event we know something happened and we just
    # ignore the heartbeat (that's why we use elif)
    elif 'heartbeat' in data:
      heartbeat = data['heartbeat']
      info("%s: event heartbeat" % heartbeat['time'])
    else:
      warn("Unknown data successfully received")


  def on_error(self, data):
    # TODO: find out if a timestamp is delived here
    error("an error occurred: %s" % data)
    self.disconnect()
