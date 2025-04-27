import time, traceback
from datetime import datetime, timezone

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

print(f"{now()}  [BOOT] Iniciando bot…  (si ves esto, Python arrancó)")

try:
    import ccxt
    print(f"{now()}  [BOOT] ccxt importado OK")
    
    exchange = ccxt.binance({'enableRateLimit': True})
    print(f"{now()}  [BOOT] Conexión Binance creada OK")
    
    pairs = {
        'BTC/USDT': None,
        'ETH/BTC' : None,
        'ETH/USDT': None
    }
    fee        = 0.001
    first_run  = True

    def fetch_prices():
        for pair in pairs:
            t = exchange.fetch_ticker(pair)
            pairs[pair] = {'bid': t['bid'], 'ask': t['ask']}

    def simulate(amount=1000):
        global first_run
        usdt0  = amount
        # ruta 1
        btc    = (usdt0 / pairs['BTC/USDT']['ask']) * (1-fee)
        eth    = (btc   / pairs['ETH/BTC']['ask'])   * (1-fee)
        usdt1  = (eth   * pairs['ETH/USDT']['bid'])  * (1-fee)
        p1     = usdt1 - usdt0
        # ruta 2
        eth2   = (usdt0 / pairs['ETH/USDT']['ask']) * (1-fee)
        btc2   = (eth2  * pairs['ETH/BTC']['bid'])  * (1-fee)
        usdt2  = (btc2  * pairs['BTC/USDT']['bid']) * (1-fee)
        p2     = usdt2 - usdt0

        if first_run:
            print(f"{now()}  === Precios iniciales ===")
            for pr in pairs:
                print(f"{now()}  {pr}  Bid:{pairs[pr]['bid']}  Ask:{pairs[pr]['ask']}")
            print(f"{now()}  [Primera] Ruta1 Profit:{p1:.4f}")
            print(f"{now()}  [Primera] Ruta2 Profit:{p2:.4f}")
            print(f"{now()}  =========================")
            first_run = False

        if p1 > 0:
            print(f"{now()}  [GANANCIA] Ruta1 Profit:{p1:.4f}")
        if p2 > 0:
            print(f"{now()}  [GANANCIA] Ruta2 Profit:{p2:.4f}")

    while True:
        try:
            fetch_prices()
            simulate(1000)
            time.sleep(5)
        except Exception as inner:
            print(f"{now()}  [ERROR bucle] {inner}")
            traceback.print_exc()
            time.sleep(5)

except Exception as outer:
    print(f"{now()}  [FATAL] Error al arrancar: {outer}")
    traceback.print_exc()
    # al lanzar de nuevo la excepción, Render abortará y verás todo el traceback
    raise
