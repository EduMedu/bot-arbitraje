import ccxt.async_support as ccxt, asyncio, os
from .config import FEE, START_USDT, TRIANGLES

def _inv(p):         # inversión segura
    return 0 if p == 0 else 1 / p

class PriceFetcher:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'apiKey' : os.getenv("BINANCE_API_KEY"),
            'secret': os.getenv("BINANCE_API_SECRET"),
        })

        # ── cargar markets una sola vez ─────────────────
        self.markets = asyncio.get_event_loop().run_until_complete(
            self.exchange.load_markets()
        )

        # construir set de pares que **sí existen**
        raw_pairs = {f"{a}/{b}" for t in TRIANGLES for a, b in
                     ((t[1], t[0]), (t[2], t[1]), (t[2], t[0]))}

        self.pairs = set()
        for p in raw_pairs:
            if p in self.markets:
                self.pairs.add(p)
            else:
                # si no existe directamente, guarda el inverso
                base, quote = p.split("/")
                inv = f"{quote}/{base}"
                if inv in self.markets:
                    self.pairs.add(inv)
        # ────────────────────────────────────────────────

        self.fee  = FEE
        self.min_profit_threshold = self.fee * 1.25

    # -------- fee dinámico ----------
    async def refresh_fee(self):
        if self.exchange.apiKey:
            try:
                info  = await self.exchange.fetch_trading_fee("BTC/USDT")
                self.fee = info['taker']
                self.min_profit_threshold = self.fee * 1.25
            except Exception:
                pass
    # --------------------------------

    async def get_prices(self):
        await self.refresh_fee()
        tickers = await self.exchange.fetch_tickers(list(self.pairs))
        return {k: {'bid': v['bid'], 'ask': v['ask']} for k, v in tickers.items()}

    # ---------- price helper ----------
    def price(self, book, base, quote, side):
        direct  = f"{quote}/{base}"
        inverse = f"{base}/{quote}"

        if direct in book and book[direct][side]:
            return book[direct][side]
        if inverse in book and book[inverse]:
            return _inv(book[inverse]['bid'] if side == "ask" else book[inverse]['ask'])
        raise KeyError(f"sin precio {base}->{quote}")
    # -----------------------------------

    # -------- profit -------------------
    def tri_profit(self, book, base, a, b):
        a_amt  = (START_USDT / self.price(book, base, a, "ask")) * (1 - self.fee)
        b_amt  = (a_amt       / self.price(book, a,   b, "ask")) * (1 - self.fee)
        base_f = (b_amt       * self.price(book, base, b, "bid")) * (1 - self.fee)
        return base_f - START_USDT
    # -----------------------------------
