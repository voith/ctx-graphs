import requests
from sqlalchemy.orm import Session

from models import TransferEvent, engine


def save_data_to_db(tx_info):
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


def crawl_graph():
    timestamp = 0
    count = 0
    while True:
        data = {
            "query": "{ transferEntities(orderBy: timestamp, first: 1000, where: {timestamp_gt: %d}) {id\n    from\n    to\n    txHash\n    amount\n    timestamp\n    blockNumber\n  }\n}" % timestamp,
            "variables": None
        }
        response = requests.post(
            "https://api.studio.thegraph.com/query/34648/ctx/v0.0.1",
            headers={"Content-Type":"application/json", "authority": "api.studio.thegraph.com"},
            json=data
        )
        if response.status_code != 200:
            print(f"received status code = {response.status_code}")
            continue
        tx_info = response.json()['data']['transferEntities']
        save_data_to_db(tx_info)
        if len(tx_info) < 1000:
            print(f"entering break statement, size tx_info={len(tx_info)}")
            if len(tx_info) > 0:
                print(f"last timestamp = {tx_info[-1]['timestamp']}")
            break
        timestamp = int(tx_info[-1]["timestamp"])
        count += 1
        print(f"count = {count}, timestamp = {timestamp}")


if __name__ == "__main__":
    crawl_graph()
