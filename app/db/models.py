from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    CheckConstraint,
    Index,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ClientStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    status: Mapped[ClientStatus] = mapped_column(
        SAEnum(ClientStatus, name="client_status", native_enum=True, create_type=False),
        nullable=False,
        server_default=ClientStatus.active.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    allocations: Mapped[List["Allocation"]] = relationship(
        back_populates="client", cascade="all, delete-orphan"
    )


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))

    allocations: Mapped[List["Allocation"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )
    daily_returns: Mapped[List["DailyReturn"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )


class Allocation(Base):
    __tablename__ = "allocations"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_allocations_quantity_pos"),
        CheckConstraint("buy_price > 0", name="ck_allocations_buy_price_pos"),
        Index("ix_allocations_client_id", "client_id"),
        Index("ix_allocations_asset_id", "asset_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)

    quantity: Mapped[Numeric] = mapped_column(Numeric(20, 8), nullable=False)
    buy_price: Mapped[Numeric] = mapped_column(Numeric(20, 8), nullable=False)
    buy_date: Mapped[date] = mapped_column(Date, nullable=False)

    client: Mapped["Client"] = relationship(back_populates="allocations")
    asset: Mapped["Asset"] = relationship(back_populates="allocations")


class DailyReturn(Base):
    __tablename__ = "daily_returns"
    __table_args__ = (
        UniqueConstraint("asset_id", "date", name="uq_daily_returns_asset_date"),
        Index("ix_daily_returns_asset_id", "asset_id"),
        Index("ix_daily_returns_date", "date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    close_price: Mapped[Numeric] = mapped_column(Numeric(20, 8), nullable=False)

    asset: Mapped["Asset"] = relationship(back_populates="daily_returns")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
