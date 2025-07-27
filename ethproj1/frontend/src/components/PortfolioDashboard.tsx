'use client'

import React, { useState, useEffect } from 'react'
import { useBarterExchange } from '@/hooks/useBarterExchange'
import { useUserNFTs } from '@/hooks/useNFTContract'
import NFTCard from './NFTCard'
import LoadingSpinner from './LoadingSpinner'
import CreateTradeModal from './CreateTradeModal'

interface PortfolioDashboardProps {
  address?: `0x${string}`
}

interface FinancialNFT {
  contractAddress: string
  tokenId: string
  name: string
  description: string
  netValue?: number
  lastUpdated?: Date
}

const PortfolioDashboard: React.FC<PortfolioDashboardProps> = ({ address }) => {
  const [selectedNFT, setSelectedNFT] = useState<FinancialNFT | null>(null)
  const [showCreateTrade, setShowCreateTrade] = useState(false)

  const { contractAddress, userTradeIds } = useBarterExchange()
  const { nfts, loading, error } = useUserNFTs()

  const handleCreateTrade = (nft: FinancialNFT) => {
    setSelectedNFT(nft)
    setShowCreateTrade(true)
  }

  const totalPortfolioValue = nfts.reduce((sum, nft) => sum + (nft.netValue || 0), 0)

  if (loading) {
    return (
      <div className="flex justify-center items-center py-16">
        <LoadingSpinner />
        <span className="ml-3 text-gray-600">Loading your portfolio...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card text-center py-12">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load portfolio</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="btn-primary"
        >
          Retry
        </button>
      </div>
    )
  }

  if (nfts.length === 0) {
    return (
      <div className="space-y-8">
        {/* Portfolio Summary */}
        <div className="card">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Your Financial NFT Portfolio
              </h1>
              <p className="text-gray-600">
                Connected wallet: {address}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Total Portfolio Value</p>
              <p className="text-3xl font-bold text-green-600">$0.00</p>
            </div>
          </div>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 border border-blue-200 rounded-lg">
              <p className="text-2xl font-bold text-blue-600">0</p>
              <p className="text-sm text-gray-600">Financial NFTs</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-2xl font-bold text-green-600">$0</p>
              <p className="text-sm text-gray-600">Avg. Position Size</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-2xl font-bold text-purple-600">0</p>
              <p className="text-sm text-gray-600">Active Trades</p>
            </div>
          </div>
        </div>

        {/* Simple Empty State */}
        <div className="card text-center py-12">
          <p className="text-gray-600">No Financial NFTs found in your wallet.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Portfolio Summary */}
      <div className="card">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Your Financial NFT Portfolio
            </h1>
            <p className="text-gray-600">
              Connected wallet: {address}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500 mb-1">Total Portfolio Value</p>
            <p className="text-3xl font-bold text-green-600">
              ${totalPortfolioValue.toLocaleString('en-US', { 
                minimumFractionDigits: 2,
                maximumFractionDigits: 2 
              })}
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-blue-600">{nfts.length}</p>
            <p className="text-sm text-blue-800">Financial NFTs</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-green-600">
              ${(totalPortfolioValue / nfts.length).toLocaleString('en-US', { 
                minimumFractionDigits: 0,
                maximumFractionDigits: 0 
              })}
            </p>
            <p className="text-sm text-green-800">Avg. Position Size</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-2xl font-bold text-purple-600">0</p>
            <p className="text-sm text-purple-800">Active Trades</p>
          </div>
        </div>
      </div>

      {/* NFT Grid */}
      {nfts.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {nfts.map((nft, index) => (
            <NFTCard
              key={`${nft.contractAddress}-${nft.tokenId}`}
              nft={nft}
              onCreateTrade={() => handleCreateTrade(nft)}
            />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Financial NFTs found</h3>
          <p className="text-gray-600">
            Connect a wallet with Financial NFTs to see your portfolio here.
          </p>
        </div>
      )}

      {/* Create Trade Modal */}
      {showCreateTrade && selectedNFT && (
        <CreateTradeModal
          nft={selectedNFT}
          onClose={() => {
            setShowCreateTrade(false)
            setSelectedNFT(null)
          }}
        />
      )}
    </div>
  )
}

export default PortfolioDashboard 