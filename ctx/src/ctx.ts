import { BigInt } from "@graphprotocol/graph-ts"
import {
  CTX,
  Approval,
  DelegateChanged,
  DelegateVotesChanged,
  MinterChanged,
  Transfer
} from "../generated/CTX/CTX"
import { TransferEntity } from "../generated/schema"

// export function handleApproval(event: Approval): void {
//   // Entities can be loaded from the store using a string ID; this ID
//   // needs to be unique across all entities of the same type
//   let entity = ExampleEntity.load(event.transaction.from.toHex())
//
//   // Entities only exist after they have been saved to the store;
//   // `null` checks allow to create entities on demand
//   if (!entity) {
//     entity = new ExampleEntity(event.transaction.from.toHex())
//
//     // Entity fields can be set using simple assignments
//     entity.count = BigInt.fromI32(0)
//   }
//
//   // BigInt and BigDecimal math are supported
//   entity.count = entity.count + BigInt.fromI32(1)
//
//   // Entity fields can be set based on event parameters
//   entity.owner = event.params.owner
//   entity.spender = event.params.spender
//
//   // Entities can be written to the store with `.save()`
//   entity.save()
//
//   // Note: If a handler doesn't require existing field values, it is faster
//   // _not_ to load the entity from the store. Instead, create it fresh with
//   // `new Entity(...)`, set the fields that should be updated and save the
//   // entity back to the store. Fields that were not set or unset remain
//   // unchanged, allowing for partial updates to be applied.
//
//   // It is also possible to access smart contracts from mappings. For
//   // example, the contract that has emitted the event can be connected to
//   // with:
//   //
//   // let contract = Contract.bind(event.address)
//   //
//   // The following functions can then be called on this contract to access
//   // state variables and other data:
//   //
//   // - contract.DELEGATION_TYPEHASH(...)
//   // - contract.DOMAIN_TYPEHASH(...)
//   // - contract.PERMIT_TYPEHASH(...)
//   // - contract.allowance(...)
//   // - contract.approve(...)
//   // - contract.balanceOf(...)
//   // - contract.checkpoints(...)
//   // - contract.decimals(...)
//   // - contract.decreaseAllowance(...)
//   // - contract.delegates(...)
//   // - contract.getCurrentVotes(...)
//   // - contract.getPriorVotes(...)
//   // - contract.increaseAllowance(...)
//   // - contract.minimumTimeBetweenMints(...)
//   // - contract.mintCap(...)
//   // - contract.minter(...)
//   // - contract.mintingAllowedAfter(...)
//   // - contract.name(...)
//   // - contract.nonces(...)
//   // - contract.numCheckpoints(...)
//   // - contract.symbol(...)
//   // - contract.totalSupply(...)
//   // - contract.transfer(...)
//   // - contract.transferFrom(...)
// }

// export function handleDelegateChanged(event: DelegateChanged): void {}
//
// export function handleDelegateVotesChanged(event: DelegateVotesChanged): void {}
//
// export function handleMinterChanged(event: MinterChanged): void {}

export function handleTransfer(event: Transfer): void {
   let transferEntity = new TransferEntity(
    event.transaction.hash.toHex() + "-" + event.params.from.toHex() + "-" + event.params.to.toHex()
   )
   transferEntity.from = event.params.from.toHex()
   transferEntity.to = event.params.to.toHex()
   transferEntity.amount = event.params.amount
   transferEntity.txHash = event.transaction.hash.toHex()
   transferEntity.timestamp = event.block.timestamp
   transferEntity.blockNumber = event.block.number
   transferEntity.save()
}
