# type: ignore
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class Coin(Base):
    __tablename__ = "coin"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column()
    symbol: Mapped[str] = mapped_column()
    dashboard_id: Mapped[str] = mapped_column(ForeignKey("dashboard.id"))

    dashboard: Mapped[Dashboard] = relationship(back_populates="coins")
    info: Mapped[CoinInfo | None] = relationship(
        back_populates="coin", cascade="all, delete-orphan"
    )


class CoinInfo(Base):
    __tablename__ = "coin_info"

    id: Mapped[str] = mapped_column(ForeignKey("coin.id"), primary_key=True)
    price: Mapped[Decimal] = mapped_column()
    market_cap: Mapped[Decimal] = mapped_column()
    price_change_24h: Mapped[Decimal] = mapped_column()
    last_updated_at: Mapped[datetime] = mapped_column()

    coin: Mapped[Coin] = relationship(back_populates="info")


class Dashboard(Base):
    __tablename__ = "dashboard"

    id: Mapped[str] = mapped_column(primary_key=True, index=True)

    coins: Mapped[list[Coin]] = relationship(
        back_populates="dashboard", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dashboard_id": self.id,
            "coins": [
                {
                    "id": coin.id,
                    "name": coin.name,
                    "symbol": coin.symbol,
                    "info": {
                        "price": float(coin.info.price) if coin.info else None,
                        "market_cap": float(coin.info.market_cap) if coin.info else None,
                        "price_change_24h": float(coin.info.price_change_24h)
                        if coin.info
                        else None,
                        "last_updated_at": coin.info.last_updated_at.isoformat()
                        if coin.info
                        else None,
                    }
                    if coin.info
                    else None,
                }
                for coin in self.coins
                if self.coins
            ],
        }
