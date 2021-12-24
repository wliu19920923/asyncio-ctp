import os
from utils import is_windows

if is_windows:
    from ctp.win64 import thosttraderapi
else:
    from ctp.linux import thosttraderapi

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AuthenticateField(object):
    def __init__(self, app_id, auth_code, broker_id, investor_id):
        self.field = thosttraderapi.CThostFtdcReqAuthenticateField()
        self.field.AppID = app_id
        self.field.AuthCode = auth_code
        self.field.broker_id = broker_id
        self.field.user_id = investor_id


class UserLoginField(object):
    def __init__(self, broker_id, investor_id, password):
        self.field = thosttraderapi.CThostFtdcReqUserLoginField()
        self.field.BrokerID = broker_id
        self.field.UserID = investor_id
        self.field.Password = password


class QrySettlementInfoField(object):
    def __init__(self, broker_id, investor_id, trading_day):
        self.field = thosttraderapi.CThostFtdcQrySettlementInfoField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.TradingDay = trading_day


class SettlementInfoConfirmField(object):
    def __init__(self, broker_id, investor_id):
        self.field = thosttraderapi.CThostFtdcSettlementInfoConfirmField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id


class QryTradingAccountField(object):
    def __init__(self, broker_id, investor_id):
        self.field = thosttraderapi.CThostFtdcQryTradingAccountField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.CurrencyID = 'CNY'


class QryInvestorPositionField(object):
    def __init__(self, broker_id, investor_id, instrument_id):
        self.field = thosttraderapi.CThostFtdcQryInvestorPositionField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.InstrumentID = instrument_id


class OrderInsertField(object):
    def __init__(self, broker_id, investor_id, exchange_id, instrument_id, offset_flag, direction, price, volume):
        self.field = thosttraderapi.CThostFtdcInputOrderField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.ExchangeID = exchange_id
        self.field.InstrumentID = instrument_id
        self.field.Direction = direction
        self.field.LimitPrice = price
        self.field.VolumeTotalOriginal = volume
        self.field.OrderPriceType = thosttraderapi.THOST_FTDC_OPT_LimitPrice
        self.field.ContingentCondition = thosttraderapi.THOST_FTDC_CC_Immediately
        self.field.TimeCondition = thosttraderapi.THOST_FTDC_TC_IOC
        self.field.VolumeCondition = thosttraderapi.THOST_FTDC_VC_AV
        self.field.CombHedgeFlag = thosttraderapi.THOST_FTDC_HF_Speculation
        self.field.CombOffsetFlag = offset_flag
        self.field.ForceCloseReason = thosttraderapi.THOST_FTDC_FCC_NotForceClose
