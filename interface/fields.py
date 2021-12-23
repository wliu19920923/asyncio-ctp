from utils import is_windows

if is_windows:
    from ctp.win64 import thosttraderapi
else:
    from ctp.linux import thosttraderapi


class ReqAuthenticateField(object):
    def __init__(self, app_id, auth_code, broker_id, investor_id):
        self.field = thosttraderapi.CThostFtdcReqAuthenticateField()
        self.field.AppID = app_id
        self.field.AuthCode = auth_code
        self.field.broker_id = broker_id
        self.field.user_id = investor_id


class ReqUserLoginField(object):
    def __init__(self, broker_id, investor_id, password):
        self.field = thosttraderapi.CThostFtdcReqUserLoginField()
        self.field.BrokerID = broker_id
        self.field.UserID = investor_id
        self.field.Password = password


class ReqQrySettlementInfo(object):
    def __init__(self, broker_id, investor_id, trading_day):
        self.field = thosttraderapi.CThostFtdcQrySettlementInfoField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.TradingDay = trading_day


class ReqSettlementInfoConfirm(object):
    def __init__(self, broker_id, investor_id):
        self.field = thosttraderapi.CThostFtdcSettlementInfoConfirmField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id


class ReqQryTradingAccount(object):
    def __init__(self, broker_id, investor_id):
        self.field = thosttraderapi.CThostFtdcQryTradingAccountField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.CurrencyID = 'CNY'


class ReqQryInvestorPosition(object):
    def __init__(self, broker_id, investor_id, instrument_id):
        self.field = thosttraderapi.CThostFtdcQryInvestorPositionField()
        self.field.BrokerID = broker_id
        self.field.InvestorID = investor_id
        self.field.InstrumentID = instrument_id


class ReqOrderInsert(object):
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
