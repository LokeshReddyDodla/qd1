'use client'

import React from 'react'

interface FinancialNFT {
  contractAddress: string
  tokenId: string
  name: string
  description: string
  netValue?: number
  lastUpdated?: Date
}

interface NFTCardProps {
  nft: FinancialNFT
  onCreateTrade: () => void
}

const NFTCard: React.FC<NFTCardProps> = ({ nft, onCreateTrade }) => {
  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`
  }

  const formatTime = (date?: Date) => {
    if (!date) return 'Unknown'
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="card hover:shadow-xl transition-shadow duration-200">
      {/* Header */}
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
            {nft.name}
          </h3>
          <p className="text-sm text-gray-500">
            {formatAddress(nft.contractAddress)} #{nft.tokenId}
          </p>
        </div>
        <div className="ml-4 text-right">
          <div className="text-sm text-gray-500 mb-1">Net Value</div>
          {nft.netValue ? (
            <div className="text-xl font-bold text-green-600">
              ${nft.netValue.toLocaleString('en-US', { 
                minimumFractionDigits: 2,
                maximumFractionDigits: 2 
              })}
            </div>
          ) : (
            <div className="text-sm text-gray-400">Calculating...</div>
          )}
        </div>
      </div>

      {/* Description */}
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {nft.description}
      </p>

      {/* Footer */}
      <div className="flex justify-between items-center pt-4 border-t border-gray-100">
        <div className="text-xs text-gray-500">
          Updated: {formatTime(nft.lastUpdated)}
        </div>
        <div className="space-x-2">
          <button className="btn-secondary text-sm py-1 px-3">
            View Details
          </button>
          <button 
            className="btn-primary text-sm py-1 px-3"
            onClick={onCreateTrade}
          >
            Create Trade
          </button>
        </div>
      </div>

      {/* Live indicator */}
      <div className="absolute top-3 right-3">
        <div className="flex items-center space-x-1">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span className="text-xs text-green-600 font-medium">LIVE</span>
        </div>
      </div>

      {/* Position this relatively for the live indicator */}
      <style jsx>{`
        .card {
          position: relative;
        }
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </div>
  )
}

export default NFTCard 