import os
import pandas
from utils import is_windows

if is_windows:
    from ctp.win64 import thosttraderapi
else:
    from ctp.linux import thosttraderapi

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class UserLoginInfo(object):
    def __init__(self, session_id=0, trading_day=None, login=False):
        self.session_id = session_id
        self.trading_day = trading_day
        self.login = login


class SettlementInfo(object):
    def __init__(self, content=None, settlement_id=None, sequence_no=None, confirm_date=None, confirm_time=None):
        self.content = content
        self.settlement_id = settlement_id
        self.sequence_no = sequence_no
        self.confirm_date = confirm_date
        self.confirm_time = confirm_time


class PositionInfo(object):
    fields = ['instrument_id', 'exchange_id', 'hedge_flag', 'position_date', 'position_direction', 'total_position', 'today_position', 'yesterday_position', 'position_cost']

    def __init__(self):
        self.records = pandas.DataFrame(columns=self.fields)

    def update_or_insert(self, instrument_id, exchange_id, position_date, position_direction, total_position, today_position, yesterday_position, position_cost):
        record = dict(instrument_id=instrument_id, exchange_id=exchange_id, position_date=position_date, position_direction=position_direction, total_position=total_position, today_position=today_position, yesterday_position=yesterday_position, position_cost=position_cost)
        records = self.records.loc[(self.records['instrument_id'] == instrument_id) & (self.records['position_date'] == position_date) & (self.records['position_direction'] == position_direction)]
        if len(records.index) > 0:
            self.records.loc[records.index, self.fields] = list(record.values())
        else:
            self.records = self.records.append([record], ignore_index=True)
        return record

    def update_by_trade(self, instrument_id, exchange_id, offset_flag, direction, price, volume, multiple):
        if offset_flag == thosttraderapi.THOST_FTDC_OF_Open:
            position_cost = price * volume * multiple
            position_direction = thosttraderapi.THOST_FTDC_PD_Long if direction == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Short
            records = self.records.loc[(self.records['instrument_id'] == instrument_id) & (self.records['position_date'] == thosttraderapi.THOST_FTDC_PSD_Today) & (self.records['position_direction'] == position_direction)]
            if records:
                record = records[0]
                position_cost += record['position_cost']
                total_position = record['total_position'] + volume
                today_position = record['today_position'] + volume
                self.records.loc[records.index, ['position_cost', 'total_position', 'today_position']] = [position_cost, total_position, today_position]
            else:
                self.update_or_insert(instrument_id, exchange_id, thosttraderapi.THOST_FTDC_PSD_Today, position_direction, volume, volume, 0, position_cost)
        else:
            position_date = thosttraderapi.THOST_FTDC_PSD_History if offset_flag == thosttraderapi.THOST_FTDC_OF_CloseYesterday else thosttraderapi.THOST_FTDC_PSD_Today
            position_direction = thosttraderapi.THOST_FTDC_PD_Short if direction == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Long
            records = self.records.loc[(self.records['instrument_id'] == instrument_id) & (self.records['position_date'] == position_date) & (self.records['position_direction'] == position_direction)]
            if records:
                record = records[0]
                position_cost = record['position_cost'] - record['position_cost'] / record['total_position'] * volume
                total_position = record['total_position'] - volume
                today_position = record['today_position'] - volume
                self.update_or_insert(instrument_id, exchange_id, position_date, position_direction, total_position, today_position, record['yesterday_position'], position_cost)

    def get_total_position(self, instrument_id, position_direction):
        records = self.records.loc[(self.records['instrument_id'] == instrument_id) & (self.records['position_direction'] == position_direction)]
        return records['total_position'].sum()

    def get_today_position(self, instrument_id, position_direction):
        records = self.records.loc[(self.records['instrument_id'] == instrument_id) & self.records['position_date'] == thosttraderapi.THOST_FTDC_PSD_Today & (self.records['position_direction'] == position_direction)]
        return records['today_position'].sum()

    def get_yesterday_position(self, instrument_id, position_direction):
        return self.get_total_position(instrument_id, position_direction) - self.get_today_position(instrument_id, position_direction)

    def get_total_position_cost(self, instrument_id, position_direction):
        records = self.records.loc[(self.records['instrument_id'] == instrument_id) & self.records['position_date'] == thosttraderapi.THOST_FTDC_PSD_Today & (self.records['position_direction'] == position_direction)]
        return records['position_cost'].sum()

    def get_avg_position_cost(self, instrument_id, position_direction, multiple):
        total_position = self.get_total_position(instrument_id, position_direction)
        total_position_cost = self.get_total_position_cost(instrument_id, position_direction)
        return total_position_cost / multiple / total_position

    def query(self, instrument_id):
        return self.records.loc[self.records['instrument_id'] == instrument_id].to_dict(orient='records')


class AccountInfo(object):
    def __init__(self, available=0, frozen=0, position_profit=0, close_profit=0):
        self.available = available
        self.frozen = frozen
        self.position_profit = position_profit
        self.close_profit = close_profit

    @property
    def net_value(self):
        return self.available + self.frozen + self.position_profit

    @property
    def profit(self):
        return self.position_profit + self.close_profit


class OrderInfo(object):
    fields = ['order_ref', 'order_sys_id', 'instrument_id', 'exchange_id', 'offset_flag', 'direction', 'price', 'volume', 'volume_traded', 'volume_total', 'status']

    def __init__(self):
        self.records = pandas.DataFrame(columns=self.fields)

    def update_or_insert(self, order_ref, order_sys_id, instrument_id, exchange_id, offset_flag, direction, price, volume, volume_traded, volume_total, status):
        record = dict(order_ref=order_ref, order_sys_id=order_sys_id, instrument_id=instrument_id, exchange_id=exchange_id, offset_flag=offset_flag, direction=direction, price=price, volume=volume, volume_traded=volume_traded, volume_total=volume_total, status=status)
        records = self.records.loc[(self.records['order_sys_id'] == order_sys_id) & (self.records['exchange_id'] == exchange_id)]
        if len(records.index) > 0:
            self.records.loc[records.index, self.fields] = list(record.values())
        else:
            self.records = self.records.append([record], ignore_index=True)
        return record

    def get_current_delegate(self):
        return self.records.loc[(self.records['status'] != thosttraderapi.THOST_FTDC_OST_Canceled) & (self.records['status'] != thosttraderapi.THOST_FTDC_OST_AllTraded)].to_dict(orient='records')
