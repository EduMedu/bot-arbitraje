import ccxt.async_support as ccxt, asyncio, os
from .config import FEE, START_USDT, TRIANGLES

def _inv(p): return 0 if p == 0 else 1 / p

class PriceFetcher:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'apiKey': os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_API_SECRET")
        })
        self.pairs = {f"{x}/{y}" for y,x,z in TRIANGLES} | \
                     {f"{z}/{x}" for y,x,z in TRIANGLES} | \
                     {f"{z}/{y}" for y,x,z in TRIANGLES}
        self.fee = FEE
        self.min_profit_threshold = self.fee * 1.25

    async def refresh_fee(self):
        if self.exchange.apiKey:
            try:
                info = await self.exchange.fetch_trading_fee("BTC/USDT")
                self.fee = info['taker']
                self.min_profit_threshold = self.fee * 1.25
            except Exception:
                pass

    async def get_prices(self):
        await self.refresh_fee()
        tickers = await self.exchange.fetch_tickers(list(self.pairs))
        return {k: {'bid': v['bid'], 'ask': v['ask']} for k, v in tickers.items()}

    def price(self, book, base, quote, side):
        direct  = f"{quote}/{base}"
        inverse = f"{base}/{quote}"
        if direct in book and book[direct][side]:
            return book[direct][side]
        if inverse in book and book[inverse]:
            return _inv(book[inverse]['bid'] if side == "ask" else book[inverse]['ask'])
        raise KeyError

    def tri_profit(self, book, base, a, b):
        a_amt  = (START_USDT / self.price(book, base, a, "ask")) * (1 - self.fee)
        b_amt  = (a_amt       / self.price(book, a,   b, "ask")) * (1 - self.fee)
        base_f = (b_amt       * self.price(book, base, b, "bid")) * (1 - self.fee)
        return base_f - START_USDT
