from sqlalchemy.orm import Session
from web3 import Web3

from models import Address, engine

w3 = Web3(Web3.HTTPProvider(
    "https://eth-mainnet.alchemyapi.io/v2/iyHzyz8TNXiqlQmJ7xEoK6cCe0-pQosM"
))


def is_contract(address):
    code = w3.eth.getCode(Web3.toChecksumAddress(address))
    return bool(code)


query = """
SELECT DISTINCT val FROM ( 
    SELECT "from_" AS val FROM "TransferEvent" UNION ALL SELECT "to" FROM "TransferEvent" 
) t;
"""


def crawl_addresses():
    with Session(engine) as session:
        events = session.execute(query).all()
        for event in events:
            print(event.val)
            add = Address(
                value=event.val,
                is_contract=is_contract(event.val)
            )
            session.add(add)
        session.commit()


if __name__ == "__main__":
    crawl_addresses()
