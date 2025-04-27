import ccxt, time, csv, os, traceback
from datetime import datetime, timezone

# ---------- CONFIG ----------
FEE             = 0.001      # 0.1 % por operación
START_USDT      = 1000
SLEEP_SEC       = 5
HEARTBEAT_SEC   = 900        # 15 min
CSV_PATH        = "/data/ganancias.csv"   # 👉 carpeta del Disk
TRIANGLES = [
    ("USDT", "BTC", "ETH"),
    ("USDT", "BTC", "BNB"),
    ("USDT", "BTC", "SOL"),
    ("USDT", "ETH", "ADA"),
    ("USDT", "BTC", "XRP")
]
# --------------------------------

exchange = ccxt.binance({'enableRateLimit': True})

def now():  # ISO-8601 UTC
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

# --- pares requeridos (sin duplicados) ---
needed_pairs = set()
for base, a, b in TRIANGLES:
    needed_pairs |= {f"{a}/{base}", f"{b}/{a}", f"{b}/{base}"}
# -----------------------------------------

def fetch_prices():
    book = {}
    for pair in needed_pairs:
        try:
            t = exchange.fetch_ticker(pair)
            book[pair] = {'bid': t['bid'], 'ask': t['ask']}
        except ccxt.BadSymbol:
            pass  # si no existe, lo resolveremos con el inverso
    return book

def price(book, base, quote, side):
    direct  = f"{quote}/{base}"
    inverse = f"{base}/{quote}"
    if direct in book and book[direct][side]:
        return book[direct][side]
    if inverse in book and book[inverse]:
        inv = book[inverse]
        if side == "ask" and inv['bid']:
            return 1 / inv['bid']
        if side == "bid" and inv['ask']:
            return 1 / inv['ask']
    raise KeyError(f"no price {base}->{quote}")

def profit(book, base, a, b):
    a_amt  = (START_USDT / price(book, base, a, "ask")) * (1 - FEE)
    b_amt  = (a_amt       / price(book, a,    b, "ask")) * (1 - FEE)
    base_f = (b_amt       * price(book, base, b, "bid")) * (1 - FEE)
    return base_f - START_USDT

# ------- CSV helper -------
def ensure_csv_header():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", newline="") as f:
            csv.writer(f).writerow(["timestamp", "route", "profit"])

def log_gain(route, prof):
    ensure_csv_header()
    line = [now(), route, f"{prof:.4f}"]
    with open(CSV_PATH, "a", newline="") as f:
        csv.writer(f).writerow(line)
    print(f"{now()}  [GAIN] {route}  +{prof:.4f}", flush=True)
# --------------------------

print(f"{now()}  [BOOT] Bot con {len(TRIANGLES)} triángulos…", flush=True)

first_run = True
last_beat = time.time()

while True:
    try:
        book = fetch_prices()

        # -------- impresión solo al arrancar --------
        if first_run:
            print(f"{now()}  === Profit inicial ===", flush=True)
            for base, a, b in TRIANGLES:
                p1 = profit(book, base, a, b)
                p2 = profit(book, base, b, a)
                print(f"{now()}  {base}->{a}->{b}->{base}  {p1:+.4f}", flush=True)
                print(f"{now()}  {base}->{b}->{a}->{base}  {p2:+.4f}", flush=True)
            print(f"{now()}  =======================", flush=True)
            first_run = False
        # --------------------------------------------

        # detectar ganancias
        for base, a, b in TRIANGLES:
            p1 = profit(book, base, a, b)
            if p1 > 0:
                log_gain(f"{base}->{a}->{b}->{base}", p1)
            p2 = profit(book, base, b, a)
            if p2 > 0:
                log_gain(f"{base}->{b}->{a}->{base}", p2)

        # latido simple (sin profits)
        if time.time() - last_beat >= HEARTBEAT_SEC:
            print(f"{now()}  [HEARTBEAT] Bot activo, sin ganancias >0 en los últimos 15 min.", flush=True)
            last_beat = time.time()

        time.sleep(SLEEP_SEC)

    except Exception as e:
        print(f"{now()}  [ERROR] {e}", flush=True)
        traceback.print_exc()
        time.sleep(SLEEP_SEC)
