import requests
from sqlalchemy.orm import Session

from models import (
    RewardPaidEvent,
    StakedEvent,
    WithdrawnEvent,
    TransferEvent,
    SushiSwapBurnEvent,
    SushiSwapMintEvent,
    SushiSwapSwapEvent,
    engine
)


transfer_entities_query = """
    { 
        transferEntities(
            orderBy: timestamp, first: 1000, where: {timestamp_gt: %d}
        ) {
            id
            from
            to
            txHash
            amount
            timestamp
            blockNumber  
        }
    }
"""

reward_paid_query = """
    {
      rewardPaidEvents(
        orderBy: timestamp, first: 1000, where: {timestamp_gt: %d}
      ) {
        id
        user
        reward
        txHash
        timestamp
        blockNumber
      }
    }
"""


staked_event_query = """
    {
      stakedEvents(
        orderBy: timestamp, first: 1000, where: {timestamp_gt: %d}
      ) {
        id
        delegator
        delegatee
        amount
        txHash
        timestamp
        blockNumber
      }
    }
"""

withdrawn_event_query = """
    {
      withdrawnEvents(
        orderBy: timestamp, first: 1000, where: {timestamp_gt: %d}
      ) {
        id
        delegator
        delegatee
        amount
        txHash
        timestamp
        blockNumber
      }
    }
"""

sushiswap_burn_event_query = """
    {
      burnEvents(
        orderBy: timestamp, first: 1000, where: {timestamp_gt: %d}
      ) {
        id
        sender
        amount0
        amount1
        to
        txHash
        timestamp
        blockNumber
      }
    }
"""

sushiswap_mint_event_query = """
    {
      mintEvents(
        orderBy: timestamp, first: 1000, where: {timestamp_gt: %d}
      ) {
      id
      sender
      amount0
      amount1
      txHash
      timestamp
      blockNumber
      }
    }
"""


sushiswap_swap_event_query = """
{
  swapEvents(
    orderBy: timestamp, first: 1000, where: {timestamp_gt: %d}
  ) {
    id
    sender
    to
    amount0In
    amount1In
    amount0Out
    amount1Out
    txHash
    timestamp
    blockNumber
  }
}
"""


def save_transfer_entity_to_db(tx_info):
    with Session(engine) as session:
        for event in tx_info:
            tx_event = TransferEvent(
                id=event['id'],
                from_=event['from'],
                to=event['to'],
                tx_hash=event['txHash'],
                amount=event['amount'],
                timestamp=event['timestamp'],
                blockNumber=event['blockNumber'],
            )
            session.add(tx_event)
            session.commit()


def save_reward_paid(tx_info):
    with Session(engine) as session:
        for event in tx_info:
            reward_event = RewardPaidEvent(
                id=event['id'],
                user=event['user'],
                reward=event['reward'],
                tx_hash=event['txHash'],
                timestamp=event['timestamp'],
                blockNumber=event['blockNumber'],
            )
            session.add(reward_event)
            session.commit()


def save_staked_events(tx_info):
    with Session(engine) as session:
        for event in tx_info:
            staked_event = StakedEvent(
                id=event['id'],
                delegator=event['delegator'],
                delegatee=event['delegatee'],
                amount=event['amount'],
                tx_hash=event['txHash'],
                timestamp=event['timestamp'],
                blockNumber=event['blockNumber'],
            )
            session.add(staked_event)
            session.commit()


def save_withdrawn_events(tx_info):
    with Session(engine) as session:
        for event in tx_info:
            withdraw_event = WithdrawnEvent(
                id=event['id'],
                delegator=event['delegator'],
                delegatee=event['delegatee'],
                amount=event['amount'],
                tx_hash=event['txHash'],
                timestamp=event['timestamp'],
                blockNumber=event['blockNumber'],
            )
            session.add(withdraw_event)
            session.commit()


def save_sushi_burn_event(tx_info):
    with Session(engine) as session:
        for event in tx_info:
            burn_event = SushiSwapBurnEvent(
                id=event['id'],
                sender=event['sender'],
                to=event['to'],
                amount0=event['amount0'],
                amount1=event['amount1'],
                tx_hash=event['txHash'],
                timestamp=event['timestamp'],
                blockNumber=event['blockNumber'],
            )
            session.add(burn_event)
            session.commit()


def save_mint_event(tx_info):
    with Session(engine) as session:
        for event in tx_info:
            swap_event = SushiSwapMintEvent(
                id=event['id'],
                sender=event['sender'],
                amount0=event['amount0'],
                amount1=event['amount1'],
                tx_hash=event['txHash'],
                timestamp=event['timestamp'],
                blockNumber=event['blockNumber'],
            )
            session.add(swap_event)
            session.commit()


def save_swap_event(tx_info):
    with Session(engine) as session:
        for event in tx_info:
            reward_event = SushiSwapSwapEvent(
                id=event['id'],
                sender=event['sender'],
                to=event['to'],
                amount0In=event['amount0In'],
                amount1In=event['amount1In'],
                amount0Out=event['amount0Out'],
                amount1Out=event['amount1Out'],
                tx_hash=event['txHash'],
                timestamp=event['timestamp'],
                blockNumber=event['blockNumber'],
            )
            session.add(reward_event)
            session.commit()


def crawl_graph(query, graph_slug, graph_version, data_key, save_func):
    timestamp = 0
    count = 0
    while True:
        data = {
            "query": query % timestamp,
            "variables": None
        }
        response = requests.post(
            "https://api.studio.thegraph.com/query/34648/%s/%s" % (
                graph_slug, graph_version
            ),
            headers={
                "Content-Type": "application/json",
                "authority": "api.studio.thegraph.com"
            },
            json=data
        )
        if response.status_code != 200:
            print(f"received status code = {response.status_code}")
            continue
        tx_info = response.json()['data'][data_key]
        save_func(tx_info)
        if len(tx_info) < 1000:
            print(f"entering break statement, size tx_info={len(tx_info)}")
            if len(tx_info) > 0:
                print(f"last timestamp = {tx_info[-1]['timestamp']}")
            break
        timestamp = int(tx_info[-1]["timestamp"])
        count += 1
        print(f"count = {count}, timestamp = {timestamp}")


def crawl_transfer_entities():
    crawl_graph(
        query=transfer_entities_query,
        graph_slug="ctx",
        graph_version="v0.0.2",
        data_key='transferEntities',
        save_func=save_transfer_entity_to_db
    )


def crawl_reward_paid():
    crawl_graph(
        query=reward_paid_query,
        graph_slug="ctx_stake",
        graph_version="v0.0.2",
        data_key='rewardPaidEvents',
        save_func=save_reward_paid
    )


def crawl_staked_event():
    crawl_graph(
        query=staked_event_query,
        graph_slug="ctx_stake",
        graph_version="v0.0.2",
        data_key='stakedEvents',
        save_func=save_staked_events
    )


def crawl_withdrawn_event():
    crawl_graph(
        query=withdrawn_event_query,
        graph_slug="ctx_stake",
        graph_version="v0.0.2",
        data_key='withdrawnEvents',
        save_func=save_withdrawn_events
    )


def crawl_sushi_burn_event():
    crawl_graph(
        query=sushiswap_burn_event_query,
        graph_slug="sushiswap_ctx",
        graph_version="v0.0.2",
        data_key='burnEvents',
        save_func=save_sushi_burn_event
    )


def crawl_sushi_mint_event():
    crawl_graph(
        query=sushiswap_mint_event_query,
        graph_slug="sushiswap_ctx",
        graph_version="v0.0.2",
        data_key='mintEvents',
        save_func=save_mint_event
    )


def crawl_sushi_swap_event():
    crawl_graph(
        query=sushiswap_swap_event_query,
        graph_slug="sushiswap_ctx",
        graph_version="v0.0.2",
        data_key='swapEvents',
        save_func=save_swap_event
    )


if __name__ == "__main__":
    crawl_transfer_entities()
    crawl_sushi_burn_event()
    crawl_sushi_mint_event()
    crawl_sushi_swap_event()
