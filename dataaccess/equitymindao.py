import datetime
import pytz
from entities.equity import Equity
from dataaccess.basedao import BaseDAO
from common.tradetime import TradeTime


class EquityMinDAO(BaseDAO):

    def __init__(self):
        BaseDAO.__init__(self)

    def insert(self, records):
        query_template = """insert into equity_min (symbol,tradeTime,openPrice,highPrice,lowPrice,closePrice,volume) values ('{}','{}',{},{},{},{},{})"""
        conn = BaseDAO.get_connection()
        cursor = conn.cursor()
        for equity in records:
            query = BaseDAO.mysql_format(query_template, equity.symbol, equity.tradeTime, equity.openPrice, equity.highPrice,
                                         equity.lowPrice, equity.lastPrice, equity.volume)
            self.execute_query(query, cursor)
        conn.commit()
        conn.close()

    def get_time_and_price(self, symbol='XIV', start_time=datetime.datetime(1971, 1, 1, 0, 0, 0), end_time=datetime.datetime(9999, 1, 1, 0, 0, 0)):
        query = """select tradeTime, closePrice from equity_min where tradeTime >= '{}' and tradeTime <= '{}' and symbol = '{}' order by tradeTime""".format(start_time, end_time, symbol)
        return self.select(query)

    def add_missing_data(self, symbol='XIV', validate_date=None):
        if validate_date is None:
            validate_date = TradeTime.get_latest_trade_date()
        start_time = datetime.datetime.fromordinal(validate_date.toordinal())
        end_time = start_time + datetime.timedelta(days=1)
        rows = self.get_time_and_price(symbol, start_time, end_time)
        j = 0
        missing_records = []
        for i, time in enumerate(TradeTime.get_all_trade_min(validate_date)):
            if j >= len(rows) or rows[j][0] > time:
                if j > 0:
                    price = rows[j-1][1]
                else:
                    price = rows[0][1]
                missing_records.append(Equity(symbol, time, price, price, price, price, 0, 0))
            else:
                j = j+1
        if len(missing_records) > 0:
            self.insert(missing_records)
        return len(missing_records)

    # TODO: complete this...
    def add_missing_data_in_real_time(self, symbol='XIV', ):
        us_dt = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
        now = datetime.datetime(us_dt.year, us_dt.month, us_dt.day, us_dt.hour, us_dt.minute, us_dt.second)
        if TradeTime.is_trade_day(now.date()):
            default_start_time = datetime.datetime(now.year, now.month, now.day, 9, 30, 0)
            start_time = max(default_start_time, datetime.datetime(now.year, now.month, now.day, now.hour-1, now.minute, 0))
            if now > start_time:
                if TradeTime.is_half_trade_day(now.date()):
                    default_end_time = datetime.datetime(now.year, now.month, now.day, 13, 0, 0)
                else:
                    default_end_time = datetime.datetime(now.year, now.month, now.day, 16, 0, 0)
                end_time = min(now, default_end_time)
                if end_time > start_time:
                    minutes_count = range((end_time - start_time).seconds/60 + 1)
                    trade_minutes = map(lambda x: start_time + datetime.timedelta(minutes=x), minutes_count)
                    # print trade_minutes
                    rows = self.get_time_and_price(symbol, start_time, end_time)
                    # print rows
                    j = 0
                    missing_records = []
                    for i, time in enumerate(trade_minutes):
                        if rows[j][0] > time:
                            if j > 0:
                                price = rows[j - 1][1]
                            else:
                                price = rows[0][1]
                            missing_records.append(Equity(symbol, time, price, price, price, price, 0, 0))
                        else:
                            j = j + 1
                    if len(missing_records) > 0:
                        self.insert(missing_records)
                    return len(missing_records)


if __name__ == '__main__':
    # EquityMinDAO().add_missing_data()
    # EquityMinDAO().add_missing_data(validate_date=datetime.date(2018, 1, 19))
    EquityMinDAO().add_missing_data_in_real_time('XIV')
