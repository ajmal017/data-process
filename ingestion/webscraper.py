import json
import traceback
from abc import ABCMeta, abstractmethod
from datetime import datetime
from utils.httphelper import HttpHelper
from utils.stringhelper import string_fetch
from common.symbols import Symbols


class WebScraper(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_current_data(self, symbol):
        pass


class YahooScraper(WebScraper):

    def get_current_data(self, symbol):
        yahoo_symbol = Symbols.get_mapped_symbol(symbol)
        url = 'https://finance.yahoo.com/quote/%s/'% yahoo_symbol
        content = HttpHelper.http_get(url)
        content = string_fetch(content, 'Currency in USD', 'At close:')
        content = string_fetch(content, 'react-text', 'react-text')
        value = string_fetch(content, '-->', '<!--')
        return float(value.replace(',', ''))


class MarketWatchScraper(WebScraper):

    def get_current_data(self, symbol):
        url = 'https://www.marketwatch.com/investing/fund/%s' % symbol
        content = HttpHelper.http_get(url)
        content = string_fetch(content, 'mw-rangeBar precision=', 'Day Low')
        value = string_fetch(content, '\"last-value\">', '</span>')
        return float(value.replace(',', ''))


if __name__ == '__main__':
    print MarketWatchScraper().get_current_data('XIV')