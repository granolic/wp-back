from datetime import datetime
from typing import Optional
from uuid import UUID as pyUUID

from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

from domain.enums import BetStatus, TransactionType, WalletType
from domain.enums.deposit import DepositEntryStatus

Base = declarative_base()


class AbstractBase(Base):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(AbstractBase):
    __tablename__ = 'users'

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_activity: Mapped[Optional[datetime]]

    wallet_address: Mapped[Optional[str]]

    balances = relationship("Balance", back_populates="user")
    bets = relationship("Bet", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    deposits = relationship('DepositEntry', back_populates='user')


class Bet(AbstractBase):
    __tablename__ = 'bets'

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[pyUUID] = mapped_column(ForeignKey('users.id'))
    pair_id: Mapped[pyUUID] = mapped_column(ForeignKey('pairs.id'), index=True)
    amount: Mapped[float]
    block_number: Mapped[int] = mapped_column(index=True)
    vector: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[BetStatus] = mapped_column(SQLEnum(BetStatus), default=BetStatus.PENDING)

    user = relationship("User", back_populates="bets")
    pair = relationship("Pair", back_populates="bets")


class Transaction(AbstractBase):
    __tablename__ = 'transactions'

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tx_id: Mapped[Optional[str]] = mapped_column(unique=True)
    user_id: Mapped[pyUUID] = mapped_column(ForeignKey('users.id'))
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), index=True)
    amount: Mapped[float]

    user = relationship("User", back_populates="transactions")


class Balance(AbstractBase):
    __tablename__ = 'balances'

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[pyUUID] = mapped_column(ForeignKey('users.id'), index=True)
    balance: Mapped[float]
    token_type: Mapped[str] = mapped_column(String(50))

    user = relationship("User", back_populates="balances")


class Pair(AbstractBase):
    __tablename__ = 'pairs'

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    contract_address: Mapped[str] = mapped_column(String(255), unique=True)
    last_ratio: Mapped[float]

    bets = relationship("Bet", back_populates="pair")


class AggregatedData(AbstractBase):
    __tablename__ = 'aggregated_data'

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    block_number: Mapped[int]
    aggregated_vector: Mapped[dict] = mapped_column(JSONB)
    ordinal_present: Mapped[bool]
    aggregate_bet_amount: Mapped[float]


class AppWallet(AbstractBase):
    __tablename__ = 'app_wallets'

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    address: Mapped[str] = mapped_column(String(255))
    wallet_type: Mapped[WalletType] = mapped_column(SQLEnum(WalletType))
    balance: Mapped[float]

    deposits = relationship("DepositEntry", back_populates="app_wallet")


class DepositEntry(AbstractBase):
    __tablename__ = 'deposit_entries'

    id: Mapped[pyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    app_wallet_id: Mapped[pyUUID] = mapped_column(ForeignKey('app_wallets.id'))
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id'))

    status: Mapped[DepositEntryStatus] = mapped_column(SQLEnum(DepositEntryStatus))

    amount: Mapped[Optional[float]]
    tx_id: Mapped[Optional[str]]

    app_wallet = relationship("AppWallet", back_populates="deposits")
    user = relationship('User', back_populates='deposits')
