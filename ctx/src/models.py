from sqlalchemy import create_engine, MetaData, Column
from sqlalchemy.types import String, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
engine = create_engine('postgresql+psycopg2://:@127.0.0.1/ctx')
metadata_obj = MetaData()


class TransferEvent(Base):
    __tablename__ = 'TransferEvent'

    id = Column(String, primary_key=True)
    from_ = Column(String)
    to = Column(String)
    tx_hash = Column(String)
    amount = Column(Numeric(80))
    timestamp = Column(Numeric(80))
    blockNumber = Column(Numeric(80))


class Address(Base):
    __tablename__ = 'address'

    value = Column(String, primary_key=True)
    is_contract = Column(Boolean)


class RewardPaidEvent(Base):
    __tablename__ = 'RewardPaidEvent'

    id = Column(String, primary_key=True)
    user = Column(String)
    reward = Column(Numeric(80))
    tx_hash = Column(String)
    timestamp = Column(Numeric(80))
    blockNumber = Column(Numeric(80))


class StakedEvent(Base):
    __tablename__ = 'StakedEvent'

    id = Column(String, primary_key=True)
    delegator = Column(String)
    delegatee = Column(String)
    amount = Column(Numeric(80))
    tx_hash = Column(String)
    timestamp = Column(Numeric(80))
    blockNumber = Column(Numeric(80))


class WithdrawnEvent(Base):
    __tablename__ = 'WithdrawnEvent'

    id = Column(String, primary_key=True)
    delegator = Column(String)
    delegatee = Column(String)
    amount = Column(Numeric(80))
    tx_hash = Column(String)
    timestamp = Column(Numeric(80))
    blockNumber = Column(Numeric(80))


class SushiSwapBurnEvent(Base):
    __tablename__ = 'SushiSwapBurnEvent'

    id = Column(String, primary_key=True)
    sender = Column(String)
    to = Column(String)
    amount0 = Column(Numeric(80))
    amount1 = Column(Numeric(80))
    tx_hash = Column(String)
    timestamp = Column(Numeric(80))
    blockNumber = Column(Numeric(80))


class SushiSwapMintEvent(Base):
    __tablename__ = 'SushiSwapMintEvent'

    id = Column(String, primary_key=True)
    sender = Column(String)
    amount0 = Column(Numeric(80))
    amount1 = Column(Numeric(80))
    tx_hash = Column(String)
    timestamp = Column(Numeric(80))
    blockNumber = Column(Numeric(80))


class SushiSwapSwapEvent(Base):
    __tablename__ = 'SushiSwapSwapEvent'

    id = Column(String, primary_key=True)
    sender = Column(String)
    to = Column(String)
    amount0In = Column(Numeric(80))
    amount1In = Column(Numeric(80))
    amount0Out = Column(Numeric(80))
    amount1Out = Column(Numeric(80))
    tx_hash = Column(String)
    timestamp = Column(Numeric(80))
    blockNumber = Column(Numeric(80))


Base.metadata.create_all(engine)
