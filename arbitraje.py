
import ccxt
import time

exchange = ccxt.binance({
    'enableRateLimit': True
})

pairs = {
    'BTC/USDT': None,
    'ETH/BTC': None,
    'ETH/USDT': None
}

fee = 0.001  # 0.1% comisión

def fetch_prices():
    for pair in pairs:
        ticker = exchange.fetch_ticker(pair)
        pairs[pair] = {
            'bid': ticker['bid'],
            'ask': ticker['ask']
        }

def simulate_trade(amount=1000):
    usdt_start = amount

    # Ruta 1: USDT → BTC → ETH → USDT
    btc = (usdt_start / pairs['BTC/USDT']['ask']) * (1 - fee)
    eth = (btc / pairs['ETH/BTC']['ask']) * (1 - fee)
    usdt_final = (eth * pairs['ETH/USDT']['bid']) * (1 - fee)
    profit = usdt_final - usdt_start

    print(f"USDT → BTC → ETH → USDT | Start: {usdt_start:.2f}, End: {usdt_final:.2f}, Profit: {profit:.4f}")

    # Ruta 2: USDT → ETH → BTC → USDT
    eth2 = (usdt_start / pairs['ETH/USDT']['ask']) * (1 - fee)
    btc2 = (eth2 * pairs['ETH/BTC']['bid']) * (1 - fee)
    usdt_final2 = (btc2 * pairs['BTC/USDT']['bid']) * (1 - fee)
    profit2 = usdt_final2 - usdt_start

    print(f"USDT → ETH → BTC → USDT | Start: {usdt_start:.2f}, End: {usdt_final2:.2f}, Profit: {profit2:.4f}")

while True:
    fetch_prices()
    simulate_trade(1000)
    time.sleep(5)
