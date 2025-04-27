
import ccxt.async_support as ccxt, asyncio, math, time
from .config import FEE, TRIANGLES
class PriceFetcher:
    def __init__(self):
        self.exchange = ccxt.binance({'enableRateLimit':True})
        self.min_profit_threshold=FEE*1.25
        self.pairs=set()
        for base,a,b in TRIANGLES:
            self.pairs.update([f"{a}/{base}",f"{b}/{a}",f"{b}/{base}"])
    async def get_prices(self):
        res=await self.exchange.fetch_tickers(list(self.pairs)[:50])
        return {k:{'bid':v['bid'],'ask':v['ask']} for k,v in res.items()}
    def price(self,book,base,quote,side):
        direct=f"{quote}/{base}"
        inverse=f"{base}/{quote}"
        if direct in book and book[direct][side]:
            return book[direct][side]
        if inverse in book and book[inverse]:
            inv=book[inverse]
            return 1/ inv['bid'] if side=="ask" else 1/ inv['ask']
        raise KeyError
    def tri_profit(self,book,base,a,b):
        a_amt=(START_USDT/self.price(book,base,a,'ask'))*(1-FEE)
        b_amt=(a_amt/self.price(book,a,b,'ask'))*(1-FEE)
        base_f=(b_amt*self.price(book,base,b,'bid'))*(1-FEE)
        return base_f-START_USDT
