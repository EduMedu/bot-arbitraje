import ccxt
import time
from datetime import datetime, timezone

exchange = ccxt.binance({'enableRateLimit': True})

pairs = {
    'BTC/USDT': None,
    'ETH/BTC' : None,
    'ETH/USDT': None
}

fee        = 0.001          # 0.1 % comisión
first_run  = True           # para imprimir solo la primera vez

def now():
    """ISO-8601 en UTC para cada línea de log."""
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def fetch_prices():
    for pair in pairs:
        tkr          = exchange.fetch_ticker(pair)
        pairs[pair]  = {'bid': tkr['bid'], 'ask': tkr['ask']}

def simulate_trade(amount=1000):
    global first_run
    usdt_start = amount

    # Ruta 1: USDT → BTC → ETH → USDT
    btc        = (usdt_start / pairs['BTC/USDT']['ask']) * (1 - fee)
    eth        = (btc        / pairs['ETH/BTC']['ask'])   * (1 - fee)
    usdt_final = (eth        * pairs['ETH/USDT']['bid'])  * (1 - fee)
    profit     = usdt_final - usdt_start

    # Ruta 2: USDT → ETH → BTC → USDT
    eth2        = (usdt_start / pairs['ETH/USDT']['ask']) * (1 - fee)
    btc2        = (eth2       * pairs['ETH/BTC']['bid'])  * (1 - fee)
    usdt_final2 = (btc2       * pairs['BTC/USDT']['bid']) * (1 - fee)
    profit2     = usdt_final2 - usdt_start

    if first_run:
        print(f"{now()}  === Precios iniciales ===")
        for pair in pairs:
            print(f"{now()}  {pair}  Bid: {pairs[pair]['bid']}  Ask: {pairs[pair]['ask']}")
        print(f"{now()}  [Primera] USDT→BTC→ETH→USDT | Profit: {profit:.4f}")
        print(f"{now()}  [Primera] USDT→ETH→BTC→USDT | Profit: {profit2:.4f}")
        print(f"{now()}  ==========================")
        first_run = False

    if profit  > 0:
        print(f"{now()}  [GANANCIA] USDT→BTC→ETH→USDT | Profit: {profit:.4f}")
    if profit2 > 0:
        print(f"{now()}  [GANANCIA] USDT→ETH→BTC→USDT | Profit: {profit2:.4f}")

while True:
    try:
        fetch_prices()
        simulate_trade(1000)
        time.sleep(5)
    except Exception as e:
        print(f"{now()}  [ERROR] {e}")
        time.sleep(5)
