import json
import os

import requests
from sqlalchemy.orm import Session
from web3 import Web3

from models import engine, TCAPTransferEvent

query = """
select distinct "val" from
 (select distinct "from_" as val from "TCAPTransferEvent" 
    union all 
 select distinct "to" from "TCAPTransferEvent") t 
"""

w3 = Web3(Web3.HTTPProvider(
    f"https://eth-mainnet.alchemyapi.io/v2/{os.environ['ALCHEMY_KEY']}"
))


with open("tcap_abi.json") as f:
    tcap_abi = json.loads(f.read())


with open("uniswap_nft.json") as f:
    uniswap_nft_abi = json.loads(f.read())


with open("sushiswap_abi.json") as f:
    sushiswap_abi = json.loads(f.read())


with open("liquidity_reward_abi.json") as f:
    liquidity_reward_abi = json.loads(f.read())


TCAP_SUSHISWAP = "0xa87e2c5d5964955242989b954474ff2eb08dd2f5"
TCAP_UNISWAP = "0x11456b3750e991383bb8943118ed79c1afdee192"

TCAP_LIQUIDITY_REWARD = "0xc8bb1cd417d20116387a5e0603e195ca4f3cf59a"

tcap_contract = w3.eth.contract(
    address=w3.toChecksumAddress("0x16c52CeeCE2ed57dAd87319D91B5e3637d50aFa4"),
    abi=tcap_abi
)

uniswap_nft_contract = w3.eth.contract(
    address=w3.toChecksumAddress("0xc36442b4a4522e871399cd717abdd847ab11fe88"),
    abi=uniswap_nft_abi
)

sushiswap_contract = w3.eth.contract(
    address=w3.toChecksumAddress("0xa87e2c5d5964955242989b954474ff2eb08dd2f5"),
    abi=sushiswap_abi
)

tcap_lp = w3.eth.contract(
    address=w3.toChecksumAddress(TCAP_LIQUIDITY_REWARD),
    abi=liquidity_reward_abi
)

# https://thegraph.com/hosted-service/subgraph/uniswap/uniswap-v3
# https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3

uni_positions_query = """
{
    positions(first:1000, where: {pool: "0x11456b3750e991383bb8943118ed79c1afdee192"}) {
      id
      owner
      liquidity
    }
}
"""

uni_position_snapshot_query = """
{
    positionSnapshots(first: 1, orderBy: timestamp, where: {position: "%s"}){
        id
        owner
    }
}
"""

univ3_staker = "0xe34139463ba50bd61336e0c446bd8c0867c6fe65"

uni_staked_address = set()


def make_request(query, args, key):
    data = {
        "query": query % args,
        "variables": None
    }
    response = requests.post(
        "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
        headers={
            "Content-Type": "application/json",
            "authority": "api.thegraph.com"
        },
        json=data
    )
    return response.json()['data'][key]


def crawl_univ3_positions():
    positions = make_request(uni_positions_query, (), "positions")
    for position in positions:
        if position["owner"] != univ3_staker:
            if int(position["liquidity"]) > 0:
                # print(f"address={position['owner']} has provided liquidity")
                uni_staked_address.add(position['owner'])
        else:
            snapshot = make_request(
                uni_position_snapshot_query,
                (position["id"]),
                "positionSnapshots"
            )[0]
            if snapshot["owner"] == univ3_staker:
                raise Exception("Owner cant be Univ3 staker")
            else:
                if int(position["liquidity"]) > 0:
                    # print(f"address={snapshot['owner']} has staked in uni-v3")
                    uni_staked_address.add(snapshot['owner'])


def crawl_tcap_holders():
    crawl_univ3_positions()
    tcp_address = set()
    sushi_address = set()
    with Session(engine) as session:
        addresses = session.execute(query).all()
        for addr in addresses:
            address = w3.toChecksumAddress(addr.val)
            print(f"scanning address = {address}")
            tcap_balance = tcap_contract.functions.balanceOf(address).call() / 10.0 ** 18
            if tcap_balance > 0:
                print(f"address={address} holding tcap = {tcap_balance}")
                tcp_address.add(address)
            else:
                sushiswap_balance = sushiswap_contract.functions.balanceOf(address).call()  / 10.0 ** 18
                if sushiswap_balance > 0:
                    print(f"address={address} provided lqiuidity on Sushi = {sushiswap_balance}")
                    sushi_address.add(address)

    print("UNI stake" + "$" * 100 + "\n")
    print("\n".join(uni_staked_address))
    print("tcap address" + "#" * 100 + "\n")
    print("\n".join(tcp_address))
    print("sushi address" + "@" * 100 + "\n")
    print("\n".join(sushi_address))
    print("All address" + "@" * 100 + "\n")
    all_address = uni_staked_address.union(tcp_address).union(sushi_address)
    print("\n".join(all_address))


def crawl_tcap_sushi_lp():
    addrs = set()
    with Session(engine) as session:
        addresses = session.execute(query).all()
        for addr in addresses:
            address = w3.toChecksumAddress(addr.val)
            print(f"scanning address = {address}")
            balance = tcap_lp.functions.balanceOf(address).call()
            if balance > 0:
                addrs.add(address)
    print("%"* 100)
    print("\n".join(addrs))


if __name__ == "__main__":
    crawl_tcap_sushi_lp()
