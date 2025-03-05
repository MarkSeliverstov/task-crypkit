import os


class Config:
    DB_CONNECTION_URL: str = (
        "postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}".format(
            DB_USER=os.environ["DB_USER"],
            DB_PASSWORD=os.environ["DB_PASSWORD"],
            DB_HOST=os.environ["DB_HOST"],
            DB_NAME=os.environ["DB_NAME"],
        )
    )
    COIN_GECKO_API_KEY: str = os.environ["COIN_GECKO_API_KEY"]
    COIN_GECKO_API_BASE_URL: str = "https://api.coingecko.com/api/v3"
    DASHBOARD_ID: str = "one_dashboard_id"
    UPDATING_INTERVAL_SEC: int = 60
