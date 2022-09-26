import json
import os
from collections import defaultdict

from sqlalchemy.orm import Session
from web3 import Web3

from models import Address, engine

w3 = Web3(Web3.HTTPProvider(
    f"https://eth-mainnet.alchemyapi.io/v2/{os.environ['ALCHEMY_KEY']}"
))


with open("ctx_abi.json") as f:
    ctx_abi = json.loads(f.read())


ctx = w3.eth.contract(
    abi=ctx_abi
)(address=w3.toChecksumAddress("0x321c2fe4446c7c963dc41dd58879af648838f98d"))


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


def fetch_ctx_balance():
    with Session(engine) as session:
        addresses = session.query(Address).filter_by(is_contract=False).all()
        for addr in addresses:
            balance = ctx.functions.balanceOf(w3.toChecksumAddress(addr.value)).call() / 10 ** 18
            if balance >= 1:
                print(f"{addr.value}, {balance}")


if __name__ == "__main__":
    # unique_contacts()
    fetch_ctx_balance()
