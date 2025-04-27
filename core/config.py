# core/config.py  –  parámetros globales
FEE         = 0.001        # tu comisión real (taker)
START_USDT  = 1000         # monto base para simular
LOOP_DELAY  = 5            # seg. entre ciclos
HEARTBEAT_SEC = 900        # 15 minutos

# --- 50 triángulos recomendados ---
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
