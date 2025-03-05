import asyncio

import aiohttp
from structlog import BoundLogger, get_logger

from .coingecko_client import coin_gecko_client
from .database import database
from .model import CoinInfo, Dashboard  # type: ignore

logger: BoundLogger = get_logger(__package__)


async def update_dashboard_data() -> None:
    async with aiohttp.ClientSession() as http_session, database.session() as session:
        dashboard: Dashboard = await database.get_default_dashboard(session)

        logger.info("Updating coins info")
        for coin in dashboard.coins:
            logger.info("Getting info", id=coin.id)
            await asyncio.sleep(2)  # Inerval to avoid "To many request errors"
            while True:
                try:
                    new_coin_info: CoinInfo | None = await coin_gecko_client.get_info(
                        http_session, coin.id
                    )
                    break
                except aiohttp.ClientResponseError as error:
                    logger.info("Sleeping after error", error=error)
                    await asyncio.sleep(30)

            assert new_coin_info is not None
            if coin.info is None:
                coin.info = new_coin_info
                await session.commit()
                continue

            coin.info.price = new_coin_info.price
            coin.info.market_cap = new_coin_info.market_cap
            coin.info.price_change_24h = new_coin_info.price_change_24h
            coin.info.last_updated_at = new_coin_info.last_updated_at

        await session.commit()
        logger.info("Updated")
