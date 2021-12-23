# import os
import requests

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# REASON_CODE = {
#     4097: '网络读失败',
#     4098: '网络写失败',
#     8193: '接收心跳超时',
#     8194: '发送心跳失败',
#     8195: '收到错误报文'
# }


class Contract(object):
    origin_url = 'https://openmd.shinnytech.com/t/md/symbols/latest.json'

    def __init__(self):
        self.mapping = self._load()

    def _load(self):
        return requests.get(self.origin_url).json()

    def get_volume_multiple(self, exchange, symbol):
        key = '%s.%s' % (exchange.upper(), symbol)
        return self.mapping[key]['volume_multiple']
