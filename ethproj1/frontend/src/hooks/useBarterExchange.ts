'use client'

import { useState } from 'react'
import { useAccount, useContractRead, useNetwork } from 'wagmi'
import { BARTER_EXCHANGE_ABI, getContractAddresses, CreateTradeParams, Trade, AssetType } from '@/lib/contracts'
import { ZERO_ADDRESS } from '@/lib/constants'

export function useBarterExchange() {
  const { address } = useAccount()
  const { chain } = useNetwork()
  const contractAddresses = getContractAddresses(chain?.id || 31337)

  // Get next trade ID
  const { data: nextTradeId } = useContractRead({
    address: contractAddresses.BARTER_EXCHANGE as `0x${string}`,
    abi: BARTER_EXCHANGE_ABI,
    functionName: 'getNextTradeId',
  })

  // Get trades by lister
  const { data: userTradeIds, refetch: refetchUserTrades } = useContractRead({
    address: contractAddresses.BARTER_EXCHANGE as `0x${string}`,
    abi: BARTER_EXCHANGE_ABI,
    functionName: 'getTradesByLister',
    args: address ? [address] : undefined,
    enabled: !!address,
  })

  return {
    contractAddress: contractAddresses.BARTER_EXCHANGE,
    nextTradeId,
    userTradeIds,
    refetchUserTrades,
  }
}

// Hook for creating a trade
export function useCreateTrade() {
  const { chain } = useNetwork()
  const contractAddresses = getContractAddresses(chain?.id || 31337)
  const [isLoading, setIsLoading] = useState(false)

  const createTrade = async (params: CreateTradeParams) => {
    setIsLoading(true)
    try {
      // For now, we'll simulate the transaction
      // In a real implementation, you'd use the actual contract write
      console.log('Creating trade with params:', params)
      
      // Simulate async operation
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Return mock transaction hash
      return { hash: '0x1234567890abcdef' }
    } catch (error) {
      console.error('Error creating trade:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  return {
    createTrade,
    isLoading,
  }
}

// Hook for getting trade details
export function useTrade(tradeId: bigint | undefined) {
  const { chain } = useNetwork()
  const contractAddresses = getContractAddresses(chain?.id || 31337)

  const { data: trade, isLoading, error, refetch } = useContractRead({
    address: contractAddresses.BARTER_EXCHANGE as `0x${string}`,
    abi: BARTER_EXCHANGE_ABI,
    functionName: 'getTrade',
    args: tradeId ? [tradeId] : undefined,
    enabled: !!tradeId,
  })

  return {
    trade: trade as Trade | undefined,
    isLoading,
    error,
    refetch,
  }
}

// Hook for executing a trade
export function useExecuteTrade() {
  const [isLoading, setIsLoading] = useState(false)

  const executeTrade = async (tradeId: bigint) => {
    setIsLoading(true)
    try {
      console.log('Executing trade:', tradeId)
      
      // Simulate async operation
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Return mock transaction hash
      return { hash: '0xabcdef1234567890' }
    } catch (error) {
      console.error('Error executing trade:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  return {
    executeTrade,
    isLoading,
  }
}

// Hook for cancelling a trade
export function useCancelTrade() {
  const [isLoading, setIsLoading] = useState(false)

  const cancelTrade = async (tradeId: bigint) => {
    setIsLoading(true)
    try {
      console.log('Cancelling trade:', tradeId)
      
      // Simulate async operation
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // Return mock transaction hash
      return { hash: '0xfedcba0987654321' }
    } catch (error) {
      console.error('Error cancelling trade:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  return {
    cancelTrade,
    isLoading,
  }
} 

// new helper inside useBarterExchange file
export function useMyTradeIds() {
  const { address } = useAccount()
  const { chain }  = useNetwork()
  const contract = getContractAddresses(chain?.id ?? 31337).BARTER_EXCHANGE

  return useContractRead({
    address: contract as `0x${string}`,
    abi: BARTER_EXCHANGE_ABI,
    functionName: 'getTradesByLister',
    args: [address ?? ZERO_ADDRESS],
    enabled: !!address,
  })
} 