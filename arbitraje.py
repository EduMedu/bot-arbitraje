import ccxt, time, traceback
from datetime import datetime, timezone

# ---------- CONFIG ----------
FEE            = 0.001      # 0.1 % por operación
START_USDT     = 1000
SLEEP_SECONDS  = 5
HEARTBEAT_SEC  = 900        # 15 minutos

TRIANGLES = [
    ("USDT", "BTC", "ETH"),
    ("USDT", "BTC", "BNB"),
    ("USDT", "BTC", "SOL"),
    ("USDT", "ETH", "ADA"),
    ("USDT", "BTC", "XRP")
]
# ----------------------------

exchange = ccxt.binance({'enableRateLimit': True})

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

# ----- construir tabla de pares necesarios -----
pairs = {}
for base, a, b in TRIANGLES:
    pairs[f"{a}/{base}"] = None
    pairs[f"{b}/{a}"]   = None
    pairs[f"{b}/{base}"] = None
# -----------------------------------------------

def fetch_prices():
    for p in pairs:
        t = exchange.fetch_ticker(p)
        pairs[p] = {'bid': t['bid'], 'ask': t['ask']}

def profit(base, a, b):
    """beneficio neto base→a→b→base (positivo = ganancia USDT)"""
    a_amt  = (START_USDT / pairs[f"{a}/{base}"]['ask']) * (1 - FEE)
    b_amt  = (a_amt       / pairs[f"{b}/{a}"]  ['ask']) * (1 - FEE)
    base_f = (b_amt       * pairs[f"{b}/{base}"]['bid']) * (1 - FEE)
    return base_f - START_USDT

def log_all_profits(tag):
    print(f"{now()}  === {tag} ===", flush=True)
    for base, a, b in TRIANGLES:
        p1 = profit(base, a, b)
        p2 = profit(base, b, a)
        print(f"{now()}  {base}->{a}->{b}->{base}  Profit:{p1:+.4f}", flush=True)
        print(f"{now()}  {base}->{b}->{a}->{base}  Profit:{p2:+.4f}", flush=True)
    print(f"{now()}  =========================", flush=True)

print(f"{now()}  [BOOT] Arrancando bot con {len(TRIANGLES)} triángulos…", flush=True)

first_run  = True
last_beat  = time.time()

while True:
    try:
        fetch_prices()

        if first_run:
            log_all_profits("Profit inicial")
            first_run = False

        # verificar ganancias y reportar
        for base, a, b in TRIANGLES:
            p1 = profit(base, a, b)
            if p1 > 0:
                print(f"{now()}  [GAIN] {base}->{a}->{b}->{base}  +{p1:.4f}", flush=True)
            p2 = profit(base, b, a)
            if p2 > 0:
                print(f"{now()}  [GAIN] {base}->{b}->{a}->{base}  +{p2:.4f}", flush=True)

        # latido cada 15 min con snapshot de beneficios
        if time.time() - last_beat >= HEARTBEAT_SEC:
            log_all_profits("Heartbeat 15 min")
            last_beat = time.time()

        time.sleep(SLEEP_SECONDS)

    except Exception as e:
        print(f"{now()}  [ERROR] {e}", flush=True)
        traceback.print_exc()
        time.sleep(SLEEP_SECONDS)
