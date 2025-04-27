
import asyncio, time, json, aiofiles, csv, os, traceback
from datetime import datetime, timezone
from .data import DataLogger
from .prices import PriceFetcher
from .config import TRIANGLES, FEE, START_USDT, LOOP_DELAY, HEARTBEAT_SEC

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

async def run_bot():
    fetcher = PriceFetcher()
    logger  = DataLogger()
    first   = True
    last    = time.time()
    while True:
        try:
            book = await fetcher.get_prices()
            if first:
                print(f"{now()}  === Profit inicial ===", flush=True)
                for base,a,b in TRIANGLES:
                    p1 = fetcher.tri_profit(book, base,a,b)
                    p2 = fetcher.tri_profit(book, base,b,a)
                    print(f"{now()}  {base}->{a}->{b}->{base} {p1:+.4f}", flush=True)
                    print(f"{now()}  {base}->{b}->{a}->{base} {p2:+.4f}", flush=True)
                print(f"{now()}  =======================", flush=True)
                first=False
            for base,a,b in TRIANGLES:
                for route in ((base,a,b),(base,b,a)):
                    try:
                        profit = fetcher.tri_profit(book,*route)
                        if profit>fetcher.min_profit_threshold:
                            await logger.log_gain("->".join(route)+(f"->{base}"),profit)
                    except Exception:
                        continue
            if time.time()-last>=HEARTBEAT_SEC:
                print(json.dumps({"ts":now(),"msg":"heartbeat"}), flush=True)
                last=time.time()
            await asyncio.sleep(LOOP_DELAY)
        except Exception as e:
            print(f"{now()} [ERROR] {e}", flush=True)
            traceback.print_exc()
            await asyncio.sleep(LOOP_DELAY)
