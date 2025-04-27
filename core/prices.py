import ccxt.async_support as ccxt
import asyncio, time
from .config import FEE, START_USDT, TRIANGLES

# ---------- helpers ----------
def _invert(price: float) -> float:
    """Evita división por cero al invertir precios."""
    return 0 if price == 0 else 1 / price
# ------------------------------

class PriceFetcher:
    """
    • Gestiona la conexión async con Binance
    • Descarga tickers por lotes
    • Calcula beneficio de un triángulo
    """
    def __init__(self):
        self.exchange = ccxt.binance({'enableRateLimit': True})
        self.pairs    = set()
        for base, a, b in TRIANGLES:
            self.pairs.update({
                f"{a}/{base}",
                f"{b}/{a}",
                f"{b}/{base}"
            })

        # umbral para filtrar ganancias pequeñas
        # (handicap de 3 legs más pequeño colchón extra)
        self.min_profit_threshold = FEE * 1.25

    # -------------- networking --------------
    async def get_prices(self) -> dict:
        """
        Devuelve dict {pair:{bid, ask}} usando fetch_tickers por lotes.
        """
        tickers = await self.exchange.fetch_tickers(list(self.pairs))
        return {p: {'bid': t['bid'], 'ask': t['ask']} for p, t in tickers.items()}
    # ----------------------------------------

    # -------------- price utils --------------
    def price(self, book, base, quote, side):
        """
        Obtiene precio ask/bid para base→quote.  
        Si no existe par directo, usa el inverso.
        """
        direct  = f"{quote}/{base}"
        inverse = f"{base}/{quote}"

        if direct in book and book[direct][side]:
            return book[direct][side]

        if inverse in book and book[inverse]:
            inv = book[inverse]
            if side == "ask" and inv['bid']:
                return _invert(inv['bid'])
            if side == "bid" and inv['ask']:
                return _invert(inv['ask'])

        raise KeyError(f"no price {base}->{quote}")
    # -----------------------------------------

    # -------------- profit -------------------
    def tri_profit(self, book, base, a, b):
        """
        Retorna beneficio neto (USDT) para: base→a→b→base
        """
        a_amt  = (START_USDT / self.price(book, base, a, "ask")) * (1 - FEE)
        b_amt  = (a_amt       / self.price(book, a,   b, "ask")) * (1 - FEE)
        base_f = (b_amt       * self.price(book, base, b, "bid")) * (1 - FEE)
        return base_f - START_USDT
    # -----------------------------------------

