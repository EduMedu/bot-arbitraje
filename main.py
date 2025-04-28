import os
import asyncio
from aiohttp import web

from core.engine import run_bot   # tu ciclo de arbitraje


# ────────────────────────────────────────────
#  Servidor HTTP  ─ GET /history
# ────────────────────────────────────────────
async def handle_history(request: web.Request) -> web.StreamResponse:
    """
    Devuelve history.csv si existe; 404 en caso contrario.
    """
    csv_path = "history.csv"
    if os.path.exists(csv_path):
        return web.FileResponse(csv_path)
    return web.Response(text="history.csv not found", status=404)


async def start_web_server() -> None:
    """
    Arranca un servidor aiohttp y permanece activo para siempre.
    El puerto se lee de la variable de entorno PORT (Render) o 8080 por defecto.
    """
    app = web.Application()
    app.router.add_get("/history", handle_history)

    port = int(os.getenv("PORT", "8080"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Mantener la tarea viva para que el servidor no termine
    await asyncio.Event().wait()


# ────────────────────────────────────────────
#  Lanzamiento conjunto: bot + web
# ────────────────────────────────────────────
async def main() -> None:
    await asyncio.gather(
        start_web_server(),  # Servidor /history
        run_bot()            # Motor de arbitraje
    )


if __name__ == "__main__":
    asyncio.run(main())
