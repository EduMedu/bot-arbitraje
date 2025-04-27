import asyncio, time, json, traceback
from datetime import datetime, timezone
from .prices import PriceFetcher
from .data import DataLogger
from .config import TRIANGLES, LOOP_DELAY, HEARTBEAT_SEC

def now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")

async def run_bot():
    fetcher = PriceFetcher()
    logger  = DataLogger()
    first   = True
    last    = time.time()

    while True:
        try:
            book = await fetcher.get_prices()

            if first:
                print(f"{now()}  === Profit inicial ===")
                for base, a, b in TRIANGLES:
                    for r in ((base,a,b),(base,b,a)):
                        try:
                            p = fetcher.tri_profit(book, *r)
                            print(f"{now()}  {'->'.join(r)}->{base} {p:+.4f}")
                        except Exception as e:
                            print(f"{now()}  [WARN] {r}: {e}")
                print(f"{now()}  =======================")
                first = False

            for base, a, b in TRIANGLES:
                for r in ((base,a,b),(base,b,a)):
                    try:
                        prof = fetcher.tri_profit(book, *r)
                        if prof > fetcher.min_profit_threshold:
                            await logger.log_gain("->".join(r)+f"->{base}", prof)
                    except Exception:
                        continue

            if time.time() - last >= HEARTBEAT_SEC:
                print(json.dumps({"ts": now(), "msg": "heartbeat"}), flush=True)
                last = time.time()

            await asyncio.sleep(LOOP_DELAY)

        except Exception as e:
            print(f"{now()}  [ERROR] {e}")
            traceback.print_exc()
            await asyncio.sleep(LOOP_DELAY)
