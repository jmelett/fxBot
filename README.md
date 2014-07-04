fxBot
=====

**fxBot** can be used to automate trading on the *FOREX* market using the
infrastructure provided by the *OANDA Corporation*. The program relies on
*OANDA's REST API*. Its main purpose is to provide a framework allowing for easy
creation, execution, and backtesting of various trading strategies.

A basic guide to setting up your *OANDA* account can be found in the [Oanda
Developer Docs](http://developer.oanda.com/docs/).


###Requirements
- **fxBot** relies on *OANDA's* [oandapy](https://github.com/oanda/oandapy)
  -- a small wrapper around the HTTP based interface.
  - **oandapy** requires the Python
    [requests](https://pypi.python.org/pypi/requests) module.
  - If you are using [Gentoo Linux](https://www.gentoo.org/), there is also an
    [ebuild](https://github.com/d-e-s-o/oandapy-ebuild) available that you can
    use directly.
