import queue
import fields
import logging
from recorders.file import AssetRecorder
from recorders.memory import OrderRecorder, PositionRecorder
from utils import is_windows, exception_catcher
from utils.server_check import check_address_port

if is_windows:
    from ctp.win64 import thosttraderapi
else:
    from ctp.linux import thosttraderapi


class TraderApi(thosttraderapi.CThostFtdcTraderSpi):
    def __init__(self, app_id, auth_code, broker_id, investor_id, password, request_id=0, logger=None):
        thosttraderapi.CThostFtdcTraderSpi.__init__(self)
        self.api = thosttraderapi.CThostFtdcTraderApi_CreateFtdcTraderApi()
        self.app_id = app_id
        self.auth_code = auth_code
        self.broker_id = broker_id
        self.investor_id = investor_id
        self.password = password
        self.queue = queue.Queue()
        self._request_id = request_id
        self.user_login_info = fields.UserLoginInfo()
        self.settlement_info = fields.SettlementInfo()
        self.logger = logger or logging

    @property
    def request_id(self):
        self._request_id += 1
        return self._request_id

    def get_balance(self):
        self.api.ReqQryTradingAccount(fields.ReqQryTradingAccount(self.broker_id, self.investor_id).field, self.request_id)

    def get_position(self, instrument_id):
        self.api.ReqQryInvestorPosition(fields.ReqQryInvestorPosition(self.broker_id, self.investor_id, instrument_id), self.request_id)

    def create_order(self, exchange_id, instrument_id, offset_flag, direction, price, volume):
        self.api.ReqOrderInsert(fields.ReqOrderInsert(self.broker_id, self.investor_id, exchange_id, instrument_id, offset_flag, direction, price, volume), self.request_id)

    def get_settlement_info(self, trading_day):
        self.api.ReqQrySettlementInfo(fields.ReqQrySettlementInfo(self.broker_id, self.investor_id, trading_day), self.request_id)

    def confirm_settlement_info(self):
        self.api.ReqSettlementInfoConfirm(fields.ReqSettlementInfoConfirm(self.broker_id, self.investor_id), self.request_id)

    def OnFrontConnected(self):
        self.api.ReqAuthenticate(fields.ReqAuthenticateField(self.app_id, self.auth_code, self.broker_id, self.investor_id), self.request_id)

    @exception_catcher
    def OnRspAuthenticate(self, pRspAuthenticateField: thosttraderapi.CThostFtdcRspAuthenticateField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise pRspInfo.ErrorMsg
        self.api.ReqUserLogin(fields.ReqUserLoginField(self.broker_id, self.investor_id, self.password), self.request_id)

    @exception_catcher
    def OnRspUserLogin(self, pRspUserLogin: thosttraderapi.CThostFtdcRspUserLoginField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise pRspInfo.ErrorMsg
        self.user_login_info = fields.UserLoginInfo(pRspUserLogin.SessionID, pRspUserLogin.TradingDay, True)

    @exception_catcher
    def OnRspQryInvestorPosition(self, pInvestorPosition: thosttraderapi.CThostFtdcInvestorPositionField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        if not pInvestorPosition:
            return
        # self.pPositionRecorder.update_or_insert(pInvestorPosition)

    @exception_catcher
    def OnRspQrySettlementInfo(self, pSettlementInfo: thosttraderapi.CThostFtdcSettlementInfoField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        self.settlement_info = fields.SettlementInfo(pSettlementInfo.Content, pSettlementInfo.SettlementID, pSettlementInfo.SequenceNo)

    @exception_catcher
    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm: thosttraderapi.CThostFtdcSettlementInfoConfirmField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        self.settlement_info.confirm_date = pSettlementInfoConfirm.ConfirmDate
        self.settlement_info.confirm_time = pSettlementInfoConfirm.ConfirmTime

    @exception_catcher
    def OnRspQryTradingAccount(self, pTradingAccount: thosttraderapi.CThostFtdcTradingAccountField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo and pRspInfo.ErrorID:
            raise TypeError(pRspInfo.ErrorMsg)
        if not pTradingAccount:
            return

            # self.pTodayProfit = round(pTradingAccount.PositionProfit + pTradingAccount.CloseProfit, 3)
            # record = self.pAssetRecorder.update_or_insert(pTradingAccount)
            # self.callback('OnRspQryTradingAccount', record)

    @exception_catcher
    def OnRspOrderInsert(self, pInputOrder: thosttraderapi.CThostFtdcInputOrderField, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pRspInfo.ErrorID == 9:
            self.confirm_settlement_info()
        raise TypeError(pRspInfo.ErrorMsg)

    @exception_catcher
    def OnRtnOrder(self, pOrder: thosttraderapi.CThostFtdcOrderField):
        if not pOrder or not pOrder.OrderSysID:
            return
            # record = self.pOrderRecorder.update_or_insert(pOrder)
        # self.callback('OnRtnOrder', (record, pOrder.SessionID != self.pSessionID and pOrder.CombOffsetFlag == thosttraderapi.THOST_FTDC_OF_Open))

    @exception_catcher
    def OnRtnTrade(self, pTrade: thosttraderapi.CThostFtdcTradeField):
        if not pTrade:
            return
            # try:
        #     self.pPositionRecorder.update_or_insert_by_trade(pTrade, self.pContracts[pTrade.InstrumentID]['multiple'])
        # except Exception as exp:
        #     self.logger.error(str(exp))

    @exception_catcher
    def OnRspError(self, pRspInfo: thosttraderapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        raise pRspInfo.ErrorMsg

    def Start(self, pszFrontAddress):
        if not check_address_port(pszFrontAddress):
            raise ConnectionError('tradeFrontAddressNotOpen')
        self.api.RegisterSpi(self)
        self.api.RegisterFront(pszFrontAddress)
        self.api.SubscribePrivateTopic(thosttraderapi.THOST_TERT_QUICK)
        self.api.SubscribePublicTopic(thosttraderapi.THOST_TERT_QUICK)
        self.api.Init()
        self.api.Join()

    def Stop(self):
        self.api.Release()
