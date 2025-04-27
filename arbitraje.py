import ccxt.async_support as ccxt
import asyncio, time, os, csv, aiofiles, traceback
from datetime import datetime, timezone

# ------------- CONFIG -------------
FEE_DEFAULT     = 0.001          # Se sobreescribe si detectamos descuento BNB
START_USDT      = 1_000
LOOP_DELAY      = 5              # segundos entre ciclos
HEARTBEAT_SEC   = 900            # 15 min
CSV_PATH        = "/data/ganancias.csv"
BATCH_SIZE      = 50             # máx 50 pares por fetch_tickers()
SEMA_LIMIT      = 10             # máx 10 peticiones simultáneas si usamos fetch_ticker
# ----------------------------------

TRIANGLES = [
    ("USDT", "BTC", "ETH"), ("USDT", "BTC", "BNB"), ("USDT", "BTC", "SOL"),
    ("USDT", "BTC", "XRP"), ("USDT", "BTC", "ADA"), ("USDT", "BTC", "DOGE"),
    ("USDT", "BTC", "TRX"), ("USDT", "BTC", "LINK"), ("USDT", "BTC", "LTC"),
    ("USDT", "BTC", "DOT"), ("USDT", "BTC", "AVAX"), ("USDT", "BTC", "MATIC"),
    ("USDT", "BTC", "ATOM"), ("USDT", "BTC", "FIL"), ("USDT", "BTC", "NEAR"),
    ("USDT", "ETH", "BNB"), ("USDT", "ETH", "SOL"), ("USDT", "ETH", "MATIC"),
    ("USDT", "ETH", "LINK"), ("USDT", "ETH", "AAVE"), ("USDT", "ETH", "UNI"),
    ("USDT", "ETH", "SAND"), ("USDT", "ETH", "MANA"), ("USDT", "ETH", "GALA"),
    ("USDT", "ETH", "ARB"), ("USDT", "BNB", "ADA"), ("USDT", "BNB", "XRP"),
    ("USDT", "BNB", "MATIC"), ("USDT", "BNB", "DOGE"), ("USDT", "BNB", "LTC"),
    ("USDT", "SOL", "DOGE"), ("USDT", "SOL", "MATIC"), ("USDT", "SOL", "AVAX"),
    ("USDT", "SOL", "APT"),  ("USDT", "SOL", "NEAR"), ("USDT", "XRP", "ADA"),
    ("USDT", "XRP", "DOGE"), ("USDT", "XRP", "TRX"), ("USDT", "ADA", "TRX"),
    ("USDT", "ADA", "MATIC"),("USDT", "ADA", "DOT"), ("USDT", "DOGE", "TRX"),
    ("USDT", "DOGE", "LTC"), ("USDT", "MATIC", "AVAX"), ("USDT", "MATIC", "ATOM"),
    ("USDT", "MATIC", "FIL"), ("USDT", "TRX", "SHIB"),("USDT", "TRX", "LTC"),
    ("USDT", "LTC", "BCH"),  ("USDT", "LTC", "ETC")
]

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")

# ---------------- CSV helpers ----------------
async def ensure_csv():
    if not os.path.exists(CSV_PATH):
        async with aiofiles.open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(await f.__aenter__())
            await writer.writerow(["timestamp", "route", "profit"])
            await f.flush()

async def log_gain(route, prof):
    await ensure_csv()
    async with aiofiles.open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(await f.__aenter__())
        await writer.writerow([now(), route, f"{prof:.4f}"])
        await f.flush()
    print(f"{now()}  [GAIN] {route}  +{prof:.4f}", flush=True)
# ---------------------------------------------

# pares necesarios
PAIRS = {f"{x}/{y}" for y, x, z in TRIANGLES}.union(
        {f"{z}/{x}" for y, x, z in TRIANGLES},
        {f"{z}/{y}" for y, x, z in TRIANGLES})

# ---------------- price helpers ----------------
def _invert(price): return 0 if price == 0 else 1 / price

def px(book, base, quote, side):
    """side = 'ask' para comprar quote con base; 'bid' para vender quote a base"""
    direct  = f"{quote}/{base}"
    inverse = f"{base}/{quote}"
    if direct in book and side in book[direct]:
        return book[direct][side]
    if inverse in book and book[inverse]:
        inv = book[inverse]
        return _invert(inv['bid'] if side == "ask" else inv['ask'])
    raise KeyError(f"Sin precio {base}->{quote}")
# -------------------------------------------------

def tri_profit(book, base, a, b, fee):
    a_amt  = (START_USDT / px(book, base, a, "ask")) * (1 - fee)
    b_amt  = (a_amt       / px(book, a,   b, "ask")) * (1 - fee)
    base_f = (b_amt       * px(book, base, b, "bid")) * (1 - fee)
    return base_f - START_USDT

async def fetch_by_batches(exchange):
    pairs = list(PAIRS)
    book  = {}
    for i in range(0, len(pairs), BATCH_SIZE):
        batch = pairs[i : i+BATCH_SIZE]
        try:
            res = await exchange.fetch_tickers(batch)
            for k, v in res.items():
                book[k] = {'bid': v['bid'], 'ask': v['ask']}
        except Exception as e:
            print(f"{now()}  [WARN] batch error {e}")
    return book

async def main():
    ex = ccxt.binance({'enableRateLimit': True})
    fee = FEE_DEFAULT
    try:
        if ex.fees and 'trading' in ex.fees and 'taker' in ex.fees['trading']:
            fee = ex.fees['trading']['taker']
    except Exception:
        pass

    first = True
    last  = time.time()

    while True:
        try:
            book = await fetch_by_batches(ex)

            if first:  # imprimir profits iniciales
                print(f"{now()}  === Profit inicial ===")
                for base, a, b in TRIANGLES:
                    try:
                        p1 = tri_profit(book, base, a, b, fee)
                        p2 = tri_profit(book, base, b, a, fee)
                        print(f"{now()}  {base}->{a}->{b}->{base}  {p1:+.4f}")
                        print(f"{now()}  {base}->{b}->{a}->{base}  {p2:+.4f}")
                    except Exception as err:
                        print(f"{now()}  [WARN] {base}-{a}-{b} {err}")
                print(f"{now()}  =======================")
                first = False

            # detección de ganancias
            for base, a, b in TRIANGLES:
                try:
                    p1 = tri_profit(book, base, a, b, fee)
                    if p1 > 0: await log_gain(f"{base}->{a}->{b}->{base}", p1)
                    p2 = tri_profit(book, base, b, a, fee)
                    if p2 > 0: await log_gain(f"{base}->{b}->{a}->{base}", p2)
                except KeyError:
                    # falta algún precio; ignoramos el triángulo en este ciclo
                    continue

            if time.time() - last >= HEARTBEAT_SEC:
                print(f"{now()}  [HEARTBEAT] activo, sin ganancias + en 15 min.", flush=True)
                last = time.time()

            await asyncio.sleep(LOOP_DELAY)

        except Exception as e:
            print(f"{now()}  [ERROR] {e}")
            traceback.print_exc()
            await asyncio.sleep(LOOP_DELAY)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        # cerramos conexiones limpias
        try:
            asyncio.get_event_loop().run_until_complete(ccxt.binance().close())
        except Exception:
            pass
