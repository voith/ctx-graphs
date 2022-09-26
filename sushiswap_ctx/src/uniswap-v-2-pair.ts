import { BigInt } from "@graphprotocol/graph-ts"
import {
  UniswapV2Pair,
  Approval,
  Burn,
  Mint,
  Swap,
  Sync,
  Transfer
} from "../generated/UniswapV2Pair/UniswapV2Pair"
import { BurnEvent, MintEvent, SwapEvent } from "../generated/schema"


export function handleBurn(event: Burn): void {
   let burnEntity = new BurnEvent(
     event.transaction.hash.toHex() +
     "-" + event.params.sender.toHex() +
     "-" + event.params.to.toHex()
   )
   burnEntity.sender = event.params.sender.toHex()
   burnEntity.to = event.params.to.toHex()
   burnEntity.amount0 = event.params.amount0
   burnEntity.amount1 = event.params.amount1
   burnEntity.txHash = event.transaction.hash.toHex()
   burnEntity.timestamp = event.block.timestamp
   burnEntity.blockNumber = event.block.number
   burnEntity.save()
}

export function handleMint(event: Mint): void {

  let MintEntity = new MintEvent(
     event.transaction.hash.toHex() + "-" + event.params.sender.toHex()
   )
   MintEntity.sender = event.params.sender.toHex()
   MintEntity.amount0 = event.params.amount0
   MintEntity.amount1 = event.params.amount1
   MintEntity.txHash = event.transaction.hash.toHex()
   MintEntity.timestamp = event.block.timestamp
   MintEntity.blockNumber = event.block.number
   MintEntity.save()

}

export function handleSwap(event: Swap): void {
    let swapEntity = new SwapEvent(
     event.transaction.hash.toHex() +
     "-" + event.params.sender.toHex() +
     "-" + event.params.to.toHex()
   )
   swapEntity.sender = event.params.sender.toHex()
   swapEntity.to = event.params.to.toHex()
   swapEntity.amount0In = event.params.amount0In
   swapEntity.amount1In = event.params.amount1In
   swapEntity.amount0Out = event.params.amount0Out
   swapEntity.amount1Out = event.params.amount1Out
   swapEntity.txHash = event.transaction.hash.toHex()
   swapEntity.timestamp = event.block.timestamp
   swapEntity.blockNumber = event.block.number
   swapEntity.save()
}
