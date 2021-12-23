from utils import is_windows, exception_catcher

if is_windows:
    from ctp.win64 import thostmduserapi
else:
    from ctp.linux import thostmduserapi


class MarketApi(thostmduserapi.CThostFtdcMdSpi):
    def __init__(self, logger):
        thostmduserapi.CThostFtdcMdSpi.__init__(self)
        self.api = thostmduserapi.CThostFtdcMdApi_CreateFtdcMdApi()
        self.subscribedContracts = list()
        self.nRequestId = 0
        self.mapping = dict()
        self.logger = logger

    def OnFrontConnected(self):
        field = thostmduserapi.CThostFtdcReqUserLoginField()
        self.api.ReqUserLogin(field, self.nRequestId)
        self.nRequestId += 1

    @exception_catcher
    def OnRspUserLogin(self, pRspUserLogin: thostmduserapi.CThostFtdcRspUserLoginField, pRspInfo: thostmduserapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        self.logger.info('登录行情服务器成功，正在请求订阅合约')
        self.api.SubscribeMarketData([contract.encode() for contract in self.subscribedContracts], len(self.subscribedContracts))

    @exception_catcher
    def OnRspSubMarketData(self, pSpecificInstrument: thostmduserapi.CThostFtdcSpecificInstrumentField, pRspInfo: thostmduserapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        if pSpecificInstrument.InstrumentID not in self.subscribedContracts:
            self.subscribedContracts.append(pSpecificInstrument.InstrumentID)

    @exception_catcher
    def OnRtnDepthMarketData(self, pDepthMarketData: thostmduserapi.CThostFtdcDepthMarketDataField):
        if pDepthMarketData.LastPrice != self.mapping[pDepthMarketData.InstrumentID]:
            self.mapping[pDepthMarketData.InstrumentID] = pDepthMarketData.LastPrice

    def OnRspError(self, pRspInfo: thostmduserapi.CThostFtdcRspInfoField, nRequestId: int, bIsLast: bool):
        self.logger.error(pRspInfo.ErrorMsg)

    def Start(self, pszFrontAddress):
        self.api.RegisterSpi(self)
        self.api.RegisterFront(pszFrontAddress)
        self.api.Init()
        self.api.Join()

    def Stop(self):
        self.api.Release()
