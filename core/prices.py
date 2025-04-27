import ccxt.async_support as ccxt, asyncio, os
from .config import FEE, START_USDT, TRIANGLES

def _inv(p):            # 1 / price con protección 0
    return 0 if p == 0 else 1 / p

class PriceFetcher:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'apiKey' : os.getenv("BINANCE_API_KEY"),
            'secret' : os.getenv("BINANCE_API_SECRET"),
        })
        # pares potenciales (directos o inversos)
        self.raw_pairs = {f"{a}/{b}" for y,a,z in TRIANGLES for b in (y,z)} | \
                         {f"{z}/{a}" for y,a,z in TRIANGLES} | \
                         {f"{z}/{y}" for y,a,z in TRIANGLES}
        self.pairs     = None            # se llenará tras load_markets
        self.fee       = FEE
        self.min_profit_threshold = self.fee * 1.25
        self._markets_loaded = False

    async def _ensure_markets(self):
        if self._markets_loaded:
            return
        markets = await self.exchange.load_markets()
        self.pairs = set()
        for p in self.raw_pairs:
            if p in markets:
                self.pairs.add(p)
            else:
                base, quote = p.split("/")
                inv = f"{quote}/{base}"
                if inv in markets:
                    self.pairs.add(inv)
        self._markets_loaded = True

    async def _refresh_fee(self):
        if self.exchange.apiKey:
            try:
                info = await self.exchange.fetch_trading_fee("BTC/USDT")
                self.fee = info["taker"]
                self.min_profit_threshold = self.fee * 1.25
            except Exception:
                pass

    async def get_prices(self):
        await self._ensure_markets()
        await self._refresh_fee()
        tickers = await self.exchange.fetch_tickers(list(self.pairs))
        return {k: {"bid": v["bid"], "ask": v["ask"]} for k, v in tickers.items()}

    # ---------------- price helper ----------------
    def price(self, book, base, quote, side):
        direct  = f"{quote}/{base}"
        inverse = f"{base}/{quote}"
        if direct in book and book[direct][side]:
            return book[direct][side]
        if inverse in book and book[inverse]:
            return _inv(book[inverse]['bid'] if side == "ask" else book[inverse]['ask'])
        raise KeyError(f"sin precio {base}->{quote}")

    # ---------------- profit calc -----------------
    def tri_profit(self, book, base, a, b):
        a_amt  = (START_USDT / self.price(book, base, a, "ask")) * (1 - self.fee)
        b_amt  = (a_amt       / self.price(book, a,   b, "ask")) * (1 - self.fee)
        base_f = (b_amt       * self.price(book, base, b, "bid")) * (1 - self.fee)
        return base_f - START_USDT
