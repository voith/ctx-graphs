from sqlalchemy import create_engine, MetaData, Column
from sqlalchemy.types import String, Numeric
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


Base.metadata.create_all(engine)
