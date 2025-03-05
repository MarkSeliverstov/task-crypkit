from datetime import datetime
from typing import Any

from aiohttp import ClientSession

from .config import Config
from .model import Coin, CoinInfo  # type: ignore


class CoinGeckoClient:
    COIN_GECKO_API_BASE_URL: str = "https://api.coingecko.com/api/v3"

    def __init__(self) -> None:
        self.api_sufix: str = f"x_cg_api_key={Config.COIN_GECKO_API_KEY}"

    async def search(self, session: ClientSession, coin_id: str) -> Coin | None:
        async with session.get(
            f"{self.COIN_GECKO_API_BASE_URL}/search?query={coin_id}&{self.api_sufix}",
            raise_for_status=True,
        ) as response:
            result: dict[str, Any] = await response.json()
        for coin in result["coins"]:
            if coin["id"] == coin_id:
                return Coin(id=coin["id"], name=coin["name"], symbol=coin["symbol"])
        return None

    async def get_info(self, session: ClientSession, id: str) -> CoinInfo | None:
        async with session.get(
            f"{self.COIN_GECKO_API_BASE_URL}/simple/price?ids={id}&vs_currencies=usd&include_market_cap=true&include_24hr_change=true&include_last_updated_at=true&{self.api_sufix}",
            raise_for_status=True,
        ) as response:
            result: dict[str, Any] = await response.json()

        if id in result:
            result_id: dict[str, str] = result[id]
            return CoinInfo(
                id=id,
                price=result_id["usd"],
                market_cap=result_id["usd_market_cap"],
                price_change_24h=result_id["usd_24h_change"],
                last_updated_at=datetime.fromtimestamp(float(result_id["last_updated_at"])),
            )
        return None


coin_gecko_client: CoinGeckoClient = CoinGeckoClient()
