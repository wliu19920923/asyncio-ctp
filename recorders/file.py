import os
from hashlib import md5
from datetime import datetime
from recorders import Recorder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AssetRecorder(object):
    fields = {'datetime': str, 'open': float, 'high': float, 'low': float, 'close': float}

    @staticmethod
    def _get_filepath(broker, user):
        text = broker + user
        filename = md5(text.encode()).hexdigest()
        return os.path.join(BASE_DIR, 'csv', 'assets', filename + '.csv')

    def _create_recorder(self, broker, user):
        filepath = self._get_filepath(broker, user)
        return Recorder(AssetRecorder.fields, filepath)

    def update_or_insert(self, pTradingAccount):
        recorder = self._create_recorder(pTradingAccount.BrokerID, pTradingAccount.AccountID)
        current_assets = round(pTradingAccount.Available + pTradingAccount.FrozenMargin + pTradingAccount.PositionProfit, 3)
        last_datetime = datetime.strptime(pTradingAccount.TradingDay + datetime.now().strftime('%H:%M'), '%Y%m%d%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        record = dict(datetime=last_datetime, open=current_assets, high=current_assets, low=current_assets, close=current_assets)
        return recorder.update_or_insert(record, datetime=last_datetime)

    def query(self, broker, user):
        recorder = self._create_recorder(broker, user)
        return recorder.records.to_dict(orient='records')
