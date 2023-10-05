from fastapi import FastAPI
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.get("/")
async def health():
    return {"status": "ok"}

@app.post("/standings/{season}/{league_id}")
async def sync_standings(season: int, league_id: int):
    logger.info(f"endpoint=/standings/{season}/{league_id}")
    return {"season": season, "league_id": league_id }

