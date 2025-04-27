import ccxt, time, traceback
from datetime import datetime, timezone

exchange = ccxt.binance({'enableRateLimit': True})

# ----- CONFIGURACIÓN -----
FEE          = 0.001          # 0.1 % por operación
START_USDT   = 1000
SLEEP        = 5              # seg. entre consultas
HEARTBEAT_SEC = 900           # 15 min
# Triángulos: (base, intermedio1, intermedio2)
TRIANGLES = [
    ("USDT", "BTC", "ETH"),   # original
    ("USDT", "BTC", "BNB"),
    ("USDT", "BTC", "SOL"),
    ("USDT", "ETH", "ADA"),
    ("USDT", "BTC", "XRP")
]
# --------------------------

def now():  # sello de tiempo ISO-8601
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

# construir el conjunto de pares necesarios
pairs = {}
for base, a, b in TRIANGLES:
    pairs[f"{a}/{base}"] = None   # ej. BTC/USDT
    pairs[f"{b}/{a}"]   = None    # ej. ETH/BTC
    pairs[f"{b}/{base}"] = None   # ej. ETH/USDT

first_run   = True
last_beat   = time.time()

def fetch_prices():
    for p in pairs:
        t = exchange.fetch_ticker(p)
        pairs[p] = {'bid': t['bid'], 'ask': t['ask']}

def profit_for_triangle(base, a, b):
    """ Calcula beneficio (base→a→b→base).  Devuelve profit neto. """
    # base → a
    a_amt  = (START_USDT / pairs[f"{a}/{base}"]['ask']) * (1-FEE)
    # a → b
    b_amt  = (a_amt       / pairs[f"{b}/{a}"]  ['ask']) * (1-FEE)
    # b → base
    base_f = (b_amt       * pairs[f"{b}/{base}"]['bid']) * (1-FEE)
    return base_f - START_USDT

def heartbeat():
    global last_beat
    if time.time() - last_beat >= HEARTBEAT_SEC:
        print(f"{now()}  [HEARTBEAT] Bot activo, sin oportunidades en los últimos 15 min.", flush=True)
        last_beat = time.time()

print(f"{now()}  [BOOT] Arrancando bot con {len(TRIANGLES)} triángulos…", flush=True)

while True:
    try:
        fetch_prices()

        if first_run:
            print(f"{now()}  === Precios iniciales ===", flush=True)
            for p in pairs:
                print(f"{now()}  {p}  Bid:{pairs[p]['bid']}  Ask:{pairs[p]['ask']}", flush=True)
            print(f"{now()}  =========================", flush=True)
            first_run = False

        for tri in TRIANGLES:
            base, a, b = tri
            prof = profit_for_triangle(base, a, b)
            if prof > 0:
                print(f"{now()}  [GAIN] {base}->{a}->{b}->{base}  Profit:{prof:.4f}", flush=True)

        heartbeat()
        time.sleep(SLEEP)

    except Exception as e:
        print(f"{now()}  [ERROR] {e}", flush=True)
        traceback.print_exc()
        time.sleep(SLEEP)
