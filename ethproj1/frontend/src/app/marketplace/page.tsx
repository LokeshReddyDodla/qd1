'use client'

import React, { useState, useEffect } from 'react'
import { useAccount } from 'wagmi'
import { useBarterExchange, useExecuteTrade } from '@/hooks/useBarterExchange'
import Header from '@/components/Header'
import LoadingSpinner from '@/components/LoadingSpinner'

interface Trade {
  tradeId: string
  lister: string
  offeredNft: {
    contract: string
    tokenId: string
    name: string
    description: string
    netValue?: number
  }
  requestedAsset: {
    contract: string
    tokenIdOrAmount: string
    type: 'NFT' | 'Token'
    symbol?: string
  }
  status: 'Open' | 'Closed' | 'Cancelled'
  createdAt: Date
}

export default function MarketplacePage() {
  const { address, isConnected } = useAccount()
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)
  const { executeTrade, isLoading: isExecuting } = useExecuteTrade()

  useEffect(() => {
    const loadTrades = async () => {
      setLoading(true)
      
      // Mock trades data - in real implementation, this would fetch from TheGraph
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockTrades: Trade[] = [
        {
          tradeId: '1',
          lister: '0x1234567890123456789012345678901234567890',
          offeredNft: {
            contract: '0xabcd...',
            tokenId: '1',
            name: 'Uniswap V3 ETH/USDC Position',
            description: 'LP position in ETH/USDC 0.3% pool',
            netValue: 2450.75
          },
          requestedAsset: {
            contract: '0xefgh...',
            tokenIdOrAmount: '2',
            type: 'NFT'
          },
          status: 'Open',
          createdAt: new Date()
        },
        {
          tradeId: '2',
          lister: '0x2345678901234567890123456789012345678901',
          offeredNft: {
            contract: '0xijkl...',
            tokenId: '5',
            name: 'Aave aUSDC Yield Token',
            description: 'Yield-bearing USDC deposit',
            netValue: 1203.50
          },
          requestedAsset: {
            contract: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
            tokenIdOrAmount: '1.5',
            type: 'Token',
            symbol: 'ETH'
          },
          status: 'Open',
          createdAt: new Date()
        }
      ]
      
      setTrades(mockTrades)
      setLoading(false)
    }

    loadTrades()
  }, [])

  const handleExecuteTrade = async (tradeId: string) => {
    try {
      const tx = await executeTrade(BigInt(tradeId))
      console.log('Trade execution transaction:', tx)
      alert('Trade executed successfully!')
      
      // Update trade status locally
      setTrades(prev => prev.map(trade => 
        trade.tradeId === tradeId 
          ? { ...trade, status: 'Closed' as const }
          : trade
      ))
    } catch (error) {
      console.error('Error executing trade:', error)
      alert('Failed to execute trade')
    }
  }

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`
  }

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center py-16">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Marketplace</h1>
            <p className="text-gray-600">Please connect your wallet to view available trades.</p>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Marketplace</h1>
          <p className="text-gray-600">Browse and execute available Financial NFT trades</p>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-16">
            <LoadingSpinner />
            <span className="ml-3 text-gray-600">Loading available trades...</span>
          </div>
        ) : (
          <div className="space-y-6">
            {trades.filter(trade => trade.status === 'Open').length > 0 ? (
              <div className="grid gap-6">
                {trades
                  .filter(trade => trade.status === 'Open')
                  .map((trade) => (
                    <div key={trade.tradeId} className="card">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="grid md:grid-cols-2 gap-6">
                            {/* Offered NFT */}
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900 mb-2">Offering</h3>
                              <div className="bg-blue-50 rounded-lg p-4">
                                <h4 className="font-medium text-blue-900">{trade.offeredNft.name}</h4>
                                <p className="text-sm text-blue-700 mb-2">{trade.offeredNft.description}</p>
                                <p className="text-xs text-blue-600">Token #{trade.offeredNft.tokenId}</p>
                                <p className="text-xs text-blue-600">Contract: {formatAddress(trade.offeredNft.contract)}</p>
                                {trade.offeredNft.netValue && (
                                  <p className="text-sm font-medium text-blue-800 mt-2">
                                    Value: ${trade.offeredNft.netValue.toLocaleString()}
                                  </p>
                                )}
                              </div>
                            </div>

                            {/* Requested Asset */}
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900 mb-2">Requesting</h3>
                              <div className="bg-green-50 rounded-lg p-4">
                                <h4 className="font-medium text-green-900">
                                  {trade.requestedAsset.type === 'NFT' ? 'NFT' : `${trade.requestedAsset.tokenIdOrAmount} ${trade.requestedAsset.symbol || 'Tokens'}`}
                                </h4>
                                <p className="text-xs text-green-600">
                                  Contract: {formatAddress(trade.requestedAsset.contract)}
                                </p>
                                {trade.requestedAsset.type === 'NFT' && (
                                  <p className="text-xs text-green-600">Token #{trade.requestedAsset.tokenIdOrAmount}</p>
                                )}
                              </div>
                            </div>
                          </div>

                          {/* Trade Info */}
                          <div className="mt-4 flex justify-between items-center text-sm text-gray-500">
                            <span>Listed by: {formatAddress(trade.lister)}</span>
                            <span>Created: {trade.createdAt.toLocaleDateString()}</span>
                          </div>
                        </div>

                        {/* Action Button */}
                        <div className="ml-6">
                          {trade.lister.toLowerCase() === address?.toLowerCase() ? (
                            <span className="text-sm text-gray-500">Your listing</span>
                          ) : (
                            <button
                              onClick={() => handleExecuteTrade(trade.tradeId)}
                              disabled={isExecuting}
                              className="btn-primary flex items-center"
                            >
                              {isExecuting ? (
                                <>
                                  <div className="loading-spinner mr-2"></div>
                                  Executing...
                                </>
                              ) : (
                                'Execute Trade'
                              )}
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            ) : (
              <div className="card text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No open trades</h3>
                <p className="text-gray-600">
                  There are currently no open trades available. Check back later or create your own listing.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
} 