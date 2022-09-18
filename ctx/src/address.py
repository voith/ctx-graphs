import os
from collections import defaultdict

from sqlalchemy.orm import Session
from web3 import Web3

from models import Address, engine

w3 = Web3(Web3.HTTPProvider(
    f"https://eth-mainnet.alchemyapi.io/v2/{os.environ['ALCHEMY_KEY']}"
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


def unique_contacts():
    seen_code = set()
    similar_contacts = defaultdict(list)
    contracts = []
    count = 0
    with Session(engine) as session:
        for addr in session.query(Address).filter_by(is_contract=True).all():
            print(f"count = {count}")
            count += 1
            code = w3.eth.getCode(Web3.toChecksumAddress(addr.value)).hex()
            if code in seen_code:
                similar_contacts[hash(code)].append(addr.value)
            else:
                seen_code.add(code)
                contracts.append(addr.value)
    print("#" * 20 + "Contracts" + "#" * 20)
    print('\n'.join(contracts))
    print("#" * 20 + "Similar contracts" + "#" * 20)
    for _hash, addresses in similar_contacts.items():
        print("*" * 20 + str(_hash) + "*" * 20)
        print('\n'.join(addresses))


if __name__ == "__main__":
    unique_contacts()
