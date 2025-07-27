'use client'

import React from 'react'
import { useAccount } from 'wagmi'
import { useMyTradeIds } from '@/hooks/useBarterExchange'
import Header from '@/components/Header'
import LoadingSpinner from '@/components/LoadingSpinner'

interface Trade {
  tradeId: bigint
  lister: string
  offeredNftContract: string
  offeredNftId: bigint
  requestedAssetContract: string
  requestedAssetIdOrAmount: bigint
  requestedAssetType: number // 0 = ERC721, 1 = ERC20
  status: number // 0 = Open, 1 = Closed, 2 = Cancelled
  createdAt: bigint
}

export default function MyTradesPage() {
  const { address, isConnected } = useAccount()
  const { data: tradeIds, isLoading, error } = useMyTradeIds()

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`
  }

  const getStatusText = (status: number) => {
    switch (status) {
      case 0: return 'Open'
      case 1: return 'Closed'
      case 2: return 'Cancelled'
      default: return 'Unknown'
    }
  }

  const getStatusColor = (status: number) => {
    switch (status) {
      case 0: return 'text-green-600 bg-green-100'
      case 1: return 'text-blue-600 bg-blue-100'
      case 2: return 'text-red-600 bg-red-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getAssetTypeText = (type: number) => {
    return type === 0 ? 'NFT' : 'Token'
  }

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center py-16">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">My Trades</h1>
            <p className="text-gray-600">Please connect your wallet to view your trades.</p>
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
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Trades</h1>
          <p className="text-gray-600">View and manage your trade listings</p>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-16">
            <LoadingSpinner />
            <span className="ml-3 text-gray-600">Loading your trades...</span>
          </div>
        ) : error ? (
          <div className="card text-center py-12">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load trades</h3>
            <p className="text-gray-600 mb-4">There was an error loading your trade history.</p>
            <button 
              onClick={() => window.location.reload()} 
              className="btn-primary"
            >
              Retry
            </button>
          </div>
        ) : !tradeIds || (Array.isArray(tradeIds) && tradeIds.length === 0) ? (
          <div className="card text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No trades found</h3>
            <p className="text-gray-600">
              You haven't created any trade listings yet. Start by creating a trade from your portfolio.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid gap-6">
              {Array.isArray(tradeIds) && tradeIds.map((tradeId: bigint) => (
                <div key={tradeId.toString()} className="card">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="grid md:grid-cols-2 gap-6">
                        {/* Offered NFT */}
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">Offering</h3>
                          <div className="bg-blue-50 rounded-lg p-4">
                            <p className="text-sm text-blue-700 mb-2">NFT Contract: {formatAddress('0x1234567890123456789012345678901234567890')}</p>
                            <p className="text-xs text-blue-600">Token ID: {tradeId.toString()}</p>
                          </div>
                        </div>

                        {/* Requested Asset */}
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 mb-2">Requesting</h3>
                          <div className="bg-green-50 rounded-lg p-4">
                            <p className="text-sm text-green-700 mb-2">Asset Contract: {formatAddress('0xabcdef1234567890abcdef1234567890abcdef12')}</p>
                            <p className="text-xs text-green-600">Asset Type: NFT</p>
                          </div>
                        </div>
                      </div>

                      {/* Trade Info */}
                      <div className="mt-4 flex justify-between items-center text-sm text-gray-500">
                        <span>Trade ID: #{tradeId.toString()}</span>
                        <span>Created: {new Date().toLocaleDateString()}</span>
                      </div>
                    </div>

                    {/* Status Badge */}
                    <div className="ml-6">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(0)}`}>
                        {getStatusText(0)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
} 