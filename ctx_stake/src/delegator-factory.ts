import { BigInt } from "@graphprotocol/graph-ts"
import {
  DelegatorFactory,
  DelegatorCreated,
  OwnershipTransferred,
  RewardAdded,
  RewardPaid,
  RewardsDurationUpdated,
  Staked,
  WaitTimeUpdated,
  Withdrawn
} from "../generated/DelegatorFactory/DelegatorFactory"
import { RewardPaidEvent, StakedEvent, WithdrawnEvent } from "../generated/schema"

export function handleRewardPaid(event: RewardPaid): void {
   let rewardEntity = new RewardPaidEvent(
     event.transaction.hash.toHex() + "-" + event.params.user.toHex()
   )
   rewardEntity.user = event.params.user.toHex()
   rewardEntity.reward = event.params.reward
   rewardEntity.txHash = event.transaction.hash.toHex()
   rewardEntity.timestamp = event.block.timestamp
   rewardEntity.blockNumber = event.block.number
   rewardEntity.save()
}


export function handleStaked(event: Staked): void {
   let stakedEntity = new StakedEvent(
     event.transaction.hash.toHex() +
     "-" + event.params.delegator.toHex() +
     "-" + event.params.delegatee.toHex()
   )
   stakedEntity.delegator = event.params.delegator.toHex()
   stakedEntity.delegatee = event.params.delegatee.toHex()
   stakedEntity.amount = event.params.amount
   stakedEntity.txHash = event.transaction.hash.toHex()
   stakedEntity.timestamp = event.block.timestamp
   stakedEntity.blockNumber = event.block.number
   stakedEntity.save()
}


export function handleWithdrawn(event: Withdrawn): void {
   let withdrawEntity = new WithdrawnEvent(
     event.transaction.hash.toHex() +
     "-" + event.params.delegator.toHex() +
     "-" + event.params.delegatee.toHex()
   )
   withdrawEntity.delegator = event.params.delegator.toHex()
   withdrawEntity.delegatee = event.params.delegatee.toHex()
   withdrawEntity.amount = event.params.amount
   withdrawEntity.txHash = event.transaction.hash.toHex()
   withdrawEntity.timestamp = event.block.timestamp
   withdrawEntity.blockNumber = event.block.number
   withdrawEntity.save()
}
