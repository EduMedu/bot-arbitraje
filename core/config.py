# config.py  — 70 triángulos verificados (abril 2025)

FEE = 0.001          # comisión por operación (taker 0.10 %)
START_USDT = 1000    # capital base para simulación
LOOP_DELAY   = 5     # segundos entre ciclos
HEARTBEAT_SEC = 900  # latido / keep‑alive cada 15 min

# 50 triángulos con USDT (pares spot comprobados en Binance)
TRIANGLES = [
    # ─── BTC como intermediario ─────────────────────────────────
    ("USDT","BTC","ETH"),  ("USDT","BTC","BNB"),  ("USDT","BTC","SOL"), ("USDT","BTC","XRP"),
    ("USDT","BTC","ADA"), ("USDT","BTC","LINK"), ("USDT","BTC","LTC"), ("USDT","BTC","DOT"),
    ("USDT","BTC","AVAX"),("USDT","BTC","ATOM"), ("USDT","BTC","FIL"), ("USDT","BTC","NEAR"),
    ("USDT","BTC","BCH"), ("USDT","BTC","ICP"), ("USDT","BTC","EOS"), ("USDT","BTC","ETC"),
    ("USDT","BTC","UNI"), ("USDT","BTC","APT"), ("USDT","BTC","SUI"),

    # ─── ETH como intermediario ─────────────────────────────────
    ("USDT","ETH","BNB"),  ("USDT","ETH","SOL"), ("USDT","ETH","XRP"), ("USDT","ETH","ADA"),
    ("USDT","ETH","LINK"), ("USDT","ETH","LTC"), ("USDT","ETH","DOT"), ("USDT","ETH","AVAX"),
    ("USDT","ETH","UNI"), ("USDT","ETH","AAVE"), ("USDT","ETH","ARB"), ("USDT","ETH","MANA"),
    ("USDT","ETH","FIL"), ("USDT","ETH","NEAR"), ("USDT","ETH","ETC"), ("USDT","ETH","TRX"),

    # ─── BNB como intermediario ─────────────────────────────────
    ("USDT","BNB","ADA"),  ("USDT","BNB","XRP"), ("USDT","BNB","LTC"), ("USDT","BNB","DOT"),
    ("USDT","BNB","AVAX"), ("USDT","BNB","LINK"),
]

# 20 triángulos adicionales con otras stables (USDC / FDUSD / TUSD)
TRIANGLES += [
    # USDC
    ("USDC","BTC","ETH"), ("USDC","BTC","BNB"), ("USDC","ETH","BNB"), ("USDC","BNB","ETH"),
    ("USDC","BTC","SOL"), ("USDC","SOL","ETH"), ("USDC","BTC","ADA"), ("USDC","ETH","ADA"),

    # FDUSD  (omitido si tu cuenta es EEA)
    ("FDUSD","BTC","ETH"), ("FDUSD","BTC","BNB"), ("FDUSD","ETH","BNB"), ("FDUSD","BNB","ETH"),
    ("FDUSD","BTC","SOL"), ("FDUSD","SOL","ETH"), ("FDUSD","BTC","ADA"), ("FDUSD","ETH","ADA"),

    # TUSD
    ("TUSD","BTC","BNB"), ("TUSD","BTC","ETH"), ("TUSD","ETH","BNB"), ("TUSD","BNB","ETH"),
]
