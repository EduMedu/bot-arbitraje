FEE = 0.001          # comisión genérica (0.10 %)
START_USDT = 1000    # capital de referencia
LOOP_DELAY = 5       # seg. entre ciclos
HEARTBEAT_SEC = 900  # latido cada 15 min

# ─────────────────────────────────────────────────────────────
# 50 triángulos válidos en Binance  (base = USDT)
# ─────────────────────────────────────────────────────────────
TRIANGLES = [

    # ----- BTC como intermediario -----
    ("USDT", "BTC", "ETH"),
    ("USDT", "BTC", "BNB"),
    ("USDT", "BTC", "SOL"),
    ("USDT", "BTC", "XRP"),
    ("USDT", "BTC", "ADA"),
    ("USDT", "BTC", "DOGE"),
    ("USDT", "BTC", "TRX"),
    ("USDT", "BTC", "LINK"),
    ("USDT", "BTC", "LTC"),
    ("USDT", "BTC", "DOT"),
    ("USDT", "BTC", "AVAX"),
    ("USDT", "BTC", "MATIC"),
    ("USDT", "BTC", "ATOM"),
    ("USDT", "BTC", "FIL"),
    ("USDT", "BTC", "NEAR"),
    ("USDT", "BTC", "ETC"),
    ("USDT", "BTC", "BCH"),
    ("USDT", "BTC", "EOS"),
    ("USDT", "BTC", "ICP"),
    ("USDT", "BTC", "UNI"),

    # ----- ETH como intermediario -----
    ("USDT", "ETH", "BNB"),
    ("USDT", "ETH", "SOL"),
    ("USDT", "ETH", "XRP"),
    ("USDT", "ETH", "ADA"),
    ("USDT", "ETH", "DOGE"),
    ("USDT", "ETH", "TRX"),
    ("USDT", "ETH", "LINK"),
    ("USDT", "ETH", "LTC"),
    ("USDT", "ETH", "DOT"),
    ("USDT", "ETH", "AVAX"),
    ("USDT", "ETH", "MATIC"),
    ("USDT", "ETH", "ATOM"),
    ("USDT", "ETH", "FIL"),
    ("USDT", "ETH", "NEAR"),
    ("USDT", "ETH", "ETC"),
    ("USDT", "ETH", "BCH"),
    ("USDT", "ETH", "UNI"),
    ("USDT", "ETH", "AAVE"),
    ("USDT", "ETH", "ARB"),

    # ----- BNB como intermediario -----
    ("USDT", "BNB", "ADA"),
    ("USDT", "BNB", "XRP"),
    ("USDT", "BNB", "LTC"),
    ("USDT", "BNB", "DOT"),
    ("USDT", "BNB", "AVAX"),
    ("USDT", "BNB", "LINK"),
    ("USDT", "BNB", "MATIC"),
    ("USDT", "BNB", "FIL"),
    ("USDT", "BNB", "TRX"),
    ("USDT", "BNB", "DOGE"),

    # ----- Otras Stable Coins (BUSD, TUSD, USDC, FDUSD)-----
    ("USDC", "BTC", "ETH"), ("USDC", "BTC", "BNB"), ("USDC", "ETH", "BNB"), ("USDC", "BNB", "ETH"),
    ("USDC", "BTC", "SOL"), ("USDC", "SOL", "ETH"), ("USDC", "BTC", "DOGE"), ("USDC", "DOGE", "ETH"),
    ("TUSD", "BTC", "BNB"), ("TUSD", "BNB", "ETH"), ("TUSD", "ETH", "BNB"), ("TUSD", "BTC", "ETH"),
    ("FDUSD", "BTC", "ETH"), ("FDUSD", "BTC", "BNB"), ("FDUSD", "ETH", "BNB"), ("FDUSD", "BNB", "ETH"),
    ("FDUSD", "BTC", "SOL"), ("FDUSD", "SOL", "ETH"), ("FDUSD", "BTC", "DOGE"), ("FDUSD", "DOGE", "ETH"),
]
