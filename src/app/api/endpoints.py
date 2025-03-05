import aiohttp
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import BoundLogger, get_logger

from ..coingecko_client import coin_gecko_client
from ..database import Database, database, get_db
from ..model import Coin, CoinInfo  # type: ignore

logger: BoundLogger = get_logger(__package__)
router: APIRouter = APIRouter(
    prefix="/coins",
    responses={404: {"description": "Not found"}},
)


@router.post("/{coin_id}")
async def create_crypto(coin_id: str, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    existed_coin: Coin | None = await db.get(Coin, coin_id)
    if existed_coin is not None:
        logger.info("Returning already existed coin")
        return JSONResponse(status_code=409, content={"error": "Coin already exists"})

    logger.info(f"Coin {coin_id} not found in the DB, searching...")
    async with aiohttp.ClientSession() as session:
        coin: Coin | None = await coin_gecko_client.search(session, coin_id)

        if coin is not None:
            logger.info(f"Coin {coin_id} found, saving into DB")
            coin.dashboard = await Database.get_default_dashboard(db)
            coin_info: CoinInfo | None = await coin_gecko_client.get_info(session, coin.id)
            if coin_info is None:
                return JSONResponse(status_code=404, content={"error": "Coin not found"})

            coin.info = coin_info
            db.add(coin)
            await db.commit()
            return JSONResponse(200)
    logger.info(f"Coin {coin_id} not found")
    return JSONResponse(status_code=404, content={"error": "Coin not found"})


@router.get("/{coin_id}", response_model=False)
async def get_crypto(coin_id: str, db: AsyncSession = Depends(get_db)) -> JSONResponse | Coin:
    existed_crypto: Coin | None = await database.get_coin_info(db, coin_id)
    if existed_crypto is not None:
        return existed_crypto
    async with aiohttp.ClientSession() as session:
        searched_crypto: Coin | None = await coin_gecko_client.search(session, coin_id)
    if searched_crypto is not None:
        return searched_crypto
    return JSONResponse(status_code=404, content={"error": "Coin not found"})


@router.delete("/{coin_id}")
async def delete_crypto(coin_id: str, db: AsyncSession = Depends(get_db)) -> JSONResponse:
    existed_crypto: Coin | None = await db.get(Coin, coin_id)

    if existed_crypto is None:
        return JSONResponse(status_code=404, content={"error": "Coin not found"})

    await db.delete(existed_crypto)
    await db.commit()

    return JSONResponse(200)
