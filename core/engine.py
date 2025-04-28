import asyncio, json, traceback, time
from datetime import datetime, timezone
from .prices import PriceFetcher
from .data   import DataLogger
from .config import TRIANGLES, LOOP_DELAY, HEARTBEAT_SEC


# ────────────────────────────────────────────────────────────
# utilidades
# ────────────────────────────────────────────────────────────
def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ────────────────────────────────────────────────────────────
# tareas asíncronas
# ────────────────────────────────────────────────────────────
async def bot_task(profit_event: asyncio.Event, profit_flag: dict):
    """
    Ciclo principal: calcula beneficios; si alguno supera el
    min_profit_threshold, lo:
      • imprime   • guarda en CSV   • marca profit_event
    """
    fetcher = PriceFetcher()
    logger  = DataLogger()
    showed_initial = False

    while True:
        try:
            book = await fetcher.get_prices()

            # ── bloque inicial: una vez ──────────────────────
            if not showed_initial:
                print(f"{now()}  === Profit inicial ===", flush=True)
                for base, a, b in TRIANGLES:
                    for r in ((base, a, b), (base, b, a)):
                        try:
                            p = fetcher.tri_profit(book, *r)
                            print(f"{now()}  {'->'.join(r)}->{base} {p:+.4f}",
                                  flush=True)
                        except Exception as e:
                            print(f"{now()}  [WARN] {r}: {e}", flush=True)
                print(f"{now()}  =======================", flush=True)
                showed_initial = True
            # ────────────────────────────────────────────────

            # ── bucle normal: registra e informa ganancias ──
            for base, a, b in TRIANGLES:
                for r in ((base, a, b), (base, b, a)):
                    try:
                        prof = fetcher.tri_profit(book, *r)
                        if prof > fetcher.min_profit_threshold:
                            route = "->".join(r) + f"->{base}"
                            print(f"{now()}  [GAIN] {route} {prof:+.4f}",
                                  flush=True)           # ← impresión inmediata
                            await logger.log_gain(route, prof)
                            profit_flag["had_profit"] = True
                            profit_event.set()         # marca ventana
                    except Exception:
                        continue
            # ────────────────────────────────────────────────

            await asyncio.sleep(LOOP_DELAY)

        except Exception as e:
            print(f"{now()}  [ERROR] {e}", flush=True)
            traceback.print_exc()
            await asyncio.sleep(LOOP_DELAY)


async def heartbeat_task(profit_event: asyncio.Event, profit_flag: dict):
    """Imprime un latido JSON cada HEARTBEAT_SEC segs con indicador de ganancias."""
    while True:
        await asyncio.sleep(HEARTBEAT_SEC)
        had = profit_flag.pop("had_profit", False)       # lee y reinicia
        print(json.dumps({"ts": now(),
                          "msg": "heartbeat",
                          "profit_window": had}),
              flush=True)
        profit_event.clear()


# ────────────────────────────────────────────────────────────
# punto de entrada (llamado desde main.py)
# ────────────────────────────────────────────────────────────
async def run_bot():
    profit_event = asyncio.Event()   # disparado cuando hay alguna ganancia
    profit_flag  = {"had_profit": False}

    await asyncio.gather(
        bot_task(profit_event, profit_flag),
        heartbeat_task(profit_event, profit_flag)
    )
