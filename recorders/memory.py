from recorders import Recorder
from utils import is_windows

if is_windows:
    from ctp.win64 import thosttraderapi
else:
    from ctp.linux import thosttraderapi


class OrderRecorder(object):
    fields = {'oid': str, 'contract': str, 'exchange': str, 'flag': str, 'direction': str, 'price': float, 'volume': int, 'volume_traded': int, 'volume_total': int, 'status': str}

    def __init__(self):
        self.recorder = Recorder(OrderRecorder.fields)

    def update_or_insert(self, pOrder):
        record = dict(oid=pOrder.OrderSysID, contract=pOrder.InstrumentID, exchange=pOrder.ExchangeID, flag=pOrder.CombOffsetFlag, direction=pOrder.Direction, price=pOrder.LimitPrice, volume=pOrder.VolumeTotalOriginal, volume_traded=pOrder.VolumeTraded, volume_total=pOrder.VolumeTotal, status=pOrder.OrderStatus)
        return self.recorder.update_or_insert(record, oid=pOrder.OrderSysID, exchange=pOrder.ExchangeID)

    def query_open_volume(self, contract, direction):
        records = self.recorder.query(contract=contract, direction=direction, flag=thosttraderapi.THOST_FTDC_OF_Open)
        return sum([item['volume_total'] for item in records if item['status'] != thosttraderapi.THOST_FTDC_OST_Canceled])

    def query_close_volume(self, contract, direction):
        records = self.recorder.query(contract=contract, direction=direction)
        return sum([item['volume_total'] for item in records if item['status'] != thosttraderapi.THOST_FTDC_OST_Canceled and item['flag'] != thosttraderapi.THOST_FTDC_OF_Open])

    def query_close_today_volume(self, contract, direction):
        records = self.recorder.query(contract=contract, direction=direction, flag=thosttraderapi.THOST_FTDC_OF_CloseToday)
        return sum([item['volume_total'] for item in records if item['status'] != thosttraderapi.THOST_FTDC_OST_Canceled])

    def query_close_yesterday_volume(self, contract, direction):
        records = self.recorder.query(contract=contract, direction=direction, flag=thosttraderapi.THOST_FTDC_OF_CloseYesterday)
        return sum([item['volume_total'] for item in records if item['status'] != thosttraderapi.THOST_FTDC_OST_Canceled])

    def query(self):
        return self.recorder.query()


class PositionRecorder(object):
    fields = {'contract': str, 'exchange': str, 'direction': str, 'date': str, 'cost': float, 'volume': int, 'today_volume': int, 'yesterday_volume': int}

    def __init__(self):
        self.recorder = Recorder(PositionRecorder.fields)

    def update_or_insert(self, pInvestorPosition):
        record = dict(contract=pInvestorPosition.InstrumentID, exchange=pInvestorPosition.ExchangeID, direction=pInvestorPosition.PosiDirection, date=pInvestorPosition.PositionDate, cost=pInvestorPosition.PositionCost, volume=pInvestorPosition.Position, today_volume=pInvestorPosition.TodayPosition, yesterday_volume=pInvestorPosition.Position - pInvestorPosition.TodayPosition)
        return self.recorder.update_or_insert(record, contract=pInvestorPosition.InstrumentID, direction=pInvestorPosition.PosiDirection, date=pInvestorPosition.PositionDate)

    def update_or_insert_by_trade(self, pTrade, multiple):
        if pTrade.OffsetFlag == thosttraderapi.THOST_FTDC_OF_Open:
            cost = pTrade.Price * pTrade.Volume * multiple
            direction = thosttraderapi.THOST_FTDC_PD_Long if pTrade.Direction == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Short
            records = self.recorder.query(contract=pTrade.InstrumentID, direction=direction, date=thosttraderapi.THOST_FTDC_PSD_Today)
            if records:
                record = records[0]
                record['cost'] += cost
                record['volume'] += pTrade.Volume
                record['today_volume'] += pTrade.Volume
            else:
                record = dict(contract=pTrade.InstrumentID, exchange=pTrade.ExchangeID, direction=direction, date=thosttraderapi.THOST_FTDC_PSD_Today, cost=cost, volume=pTrade.Volume, today_volume=pTrade.Volume, yesterday_volume=0)
            self.recorder.update_or_insert(record, contract=pTrade.InstrumentID, direction=direction, date=thosttraderapi.THOST_FTDC_PSD_Today)
        else:
            date = thosttraderapi.THOST_FTDC_PSD_History if pTrade.OffsetFlag == thosttraderapi.THOST_FTDC_OF_CloseYesterday else thosttraderapi.THOST_FTDC_PSD_Today
            direction = thosttraderapi.THOST_FTDC_PD_Short if pTrade.Direction == thosttraderapi.THOST_FTDC_D_Buy else thosttraderapi.THOST_FTDC_PD_Long
            records = self.recorder.query(contract=pTrade.InstrumentID, direction=direction, date=date)
            if records:
                record = records[0]
                record['cost'] = record['cost'] - record['cost'] / record['volume'] * pTrade.Volume
                record['volume'] -= pTrade.Volume
                record['today_volume'] -= pTrade.Volume
                self.recorder.update_or_insert(record, contract=pTrade.InstrumentID, direction=direction, date=date)

    def query_yesterday_position(self, contract, direction):
        volume = 0
        records = self.recorder.query(contract=contract, direction=direction)
        for item in records:
            if item['date'] == thosttraderapi.THOST_FTDC_PSD_Today:
                volume += item['yesterday_volume']
            else:
                volume += item['volume']
        return volume

    def query_today_position(self, contract, direction):
        records = self.recorder.query(contract=contract, direction=direction, date=thosttraderapi.THOST_FTDC_PSD_Today)
        return sum([item['today_volume'] for item in records])

    def query_total_position(self, contract, direction):
        records = self.recorder.query(contract=contract, direction=direction)
        return sum([item['today_volume'] for item in records])

    def query_total_cost(self, contract, direction):
        records = self.recorder.query(contract=contract, direction=direction)
        return sum([item['cost'] for item in records])

    def query_avg_cost(self, contract, direction, multiple):
        cost, volume = 0, 0
        records = self.recorder.query(contract=contract, direction=direction)
        for item in records:
            cost += item['cost']
            volume += item['volume']
        if cost and volume:
            return round(cost / volume / multiple, 3)
        return 0

    def query(self, **kwargs):
        return self.recorder.query(**kwargs)


class DetailRecorder(object):
    fields = {'contract': str, 'direction': str, 'order_loss_upper_limit': int, 'avg_cost': float, 'position_volume': int, 'last_price': int, 'previous_price': int, 'price_difference': int, 'strategy_should_position': int, 'profit_ratio': int}

    def __init__(self):
        self.recorder = Recorder(DetailRecorder.fields)

    def update_or_insert(self, detail):
        record = dict(contract=detail['contract'], direction=detail['direction'], order_loss_upper_limit=detail['order_loss_upper_limit'], avg_cost=detail['avg_cost'], previous_price=detail['previous_price'], position_volume=detail['position_volume'], last_price=detail['last_price'], price_difference=detail['price_difference'], strategy_should_position=detail['strategy_should_position'], profit_ratio=detail['profit_ratio'])
        return self.recorder.update_or_insert(record, contract=detail['contract'], direction=detail['direction'])
