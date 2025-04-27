
import aiofiles, csv, os, datetime, asyncio
CSV_DIR="/data"
class DataLogger:
    async def log_gain(self,route,profit):
        today=datetime.date.today().isoformat()
        path=os.path.join(CSV_DIR,f"ganancias_{today}.csv")
        os.makedirs(CSV_DIR,exist_ok=True)
        async with aiofiles.open(path,"a",newline="") as f:
            writer=csv.writer(await f.__aenter__())
            await writer.writerow([datetime.datetime.utcnow().isoformat(),route,f"{profit:.4f}"])
            await f.flush()
