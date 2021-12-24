import requests


class Contract(object):
    origin_url = 'https://openmd.shinnytech.com/t/md/symbols/latest.json'

    def __init__(self):
        self.mapping = self._load()

    def _load(self):
        return requests.get(self.origin_url).json()

    def get_volume_multiple(self, exchange, symbol):
        key = '%s.%s' % (exchange.upper(), symbol)
        return self.mapping[key]['volume_multiple']

    def get_future_list(self):
        return [self.mapping[key] for key in self.mapping if self.mapping[key]['class'] == 'FUTURE']
