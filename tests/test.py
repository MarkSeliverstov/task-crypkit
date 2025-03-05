from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.endpoints import create_crypto
from app.coingecko_client import CoinGeckoClient, coin_gecko_client


@pytest.fixture
def mock_db() -> AsyncSession:
    db = AsyncMock()
    db.get = AsyncMock(return_value=None)
    db.add = AsyncMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def mock_coin_gecko_client() -> CoinGeckoClient:
    client = AsyncMock()
    client.search = AsyncMock(return_value=MagicMock())
    client.get_info = AsyncMock(return_value=MagicMock())
    return client


@pytest.mark.asyncio
async def test_create_crypto_coin_not_in_db(
    mock_db: AsyncSession, mock_coin_gecko_client: CoinGeckoClient
) -> None:
    coin_id = "bitcoin"
    coin_gecko_client.search = mock_coin_gecko_client.search  # type: ignore
    coin_gecko_client.get_info = mock_coin_gecko_client.get_info  # type: ignore
    response = await create_crypto(coin_id, mock_db)
    assert response.status_code == 200
    mock_db.add.assert_called_once()  # type: ignore
    mock_db.commit.assert_called_once()  # type: ignore


@pytest.mark.asyncio
async def test_create_crypto_coin_exists_in_db(mock_db: AsyncSession) -> None:
    coin_id = "bitcoin"
    mock_db.get = AsyncMock(return_value={"id": "bitcoin"})  # type: ignore
    response = await create_crypto(coin_id, mock_db)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_crypto_coin_not_found(
    mock_db: AsyncSession, mock_coin_gecko_client: CoinGeckoClient
) -> None:
    coin_id = "bitcoin"
    coin_gecko_client.search = mock_coin_gecko_client.search  # type: ignore
    coin_gecko_client.get_info = AsyncMock(return_value=None)  # type: ignore
    response = await create_crypto(coin_id, mock_db)
    assert response.status_code == 404
