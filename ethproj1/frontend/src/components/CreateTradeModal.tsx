'use client'

import React, { useState } from 'react'
import { useCreateTrade } from '@/hooks/useBarterExchange'
import { useNFTApproval } from '@/hooks/useNFTContract'
import { AssetType } from '@/lib/contracts'
import { parseEther } from 'viem'

interface FinancialNFT {
  contractAddress: string
  tokenId: string
  name: string
  description: string
  netValue?: number
  lastUpdated?: Date
}

interface CreateTradeModalProps {
  nft: FinancialNFT
  onClose: () => void
}

const CreateTradeModal: React.FC<CreateTradeModalProps> = ({ nft, onClose }) => {
  const [requestedAssetType, setRequestedAssetType] = useState<AssetType>(AssetType.ERC721)
  const [requestedContract, setRequestedContract] = useState('')
  const [requestedTokenId, setRequestedTokenId] = useState('')
  const [requestedAmount, setRequestedAmount] = useState('')
  const [step, setStep] = useState<'approval' | 'trade'>('approval')

  const { createTrade, isLoading: isCreatingTrade } = useCreateTrade()
  const { approveNFT, isLoading: isApproving } = useNFTApproval()

  const handleApproval = async () => {
    try {
      const tx = await approveNFT(nft.contractAddress, BigInt(nft.tokenId))
      console.log('Approval transaction:', tx)
      setStep('trade')
      alert('NFT approved successfully! You can now create the trade.')
    } catch (error) {
      console.error('Error approving NFT:', error)
      alert('Failed to approve NFT')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      const requestedAssetIdOrAmount = requestedAssetType === AssetType.ERC721 
        ? BigInt(requestedTokenId)
        : parseEther(requestedAmount)

      const tradeParams = {
        offeredNftContract: nft.contractAddress,
        offeredNftId: BigInt(nft.tokenId),
        requestedAssetContract: requestedContract,
        requestedAssetIdOrAmount,
        requestedAssetType,
      }

      const tx = await createTrade(tradeParams)
      console.log('Trade creation transaction:', tx)
      
      alert('Trade listing created successfully!')
      onClose()
    } catch (error) {
      console.error('Error creating trade:', error)
      alert('Failed to create trade listing')
    }
  }

  const isLoading = isApproving || isCreatingTrade

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Create Trade Listing</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Offering Section */}
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">You're offering:</h3>
            <div className="text-sm">
              <p className="font-medium text-blue-800">{nft.name}</p>
              <p className="text-blue-600">Token #{nft.tokenId}</p>
              <p className="text-blue-600">Contract: {nft.contractAddress.slice(0, 6)}...{nft.contractAddress.slice(-4)}</p>
              {nft.netValue && (
                <p className="text-blue-600 font-medium">Value: ${nft.netValue.toLocaleString()}</p>
              )}
            </div>
          </div>

          {/* Step indicator */}
          <div className="mb-4">
            <div className="flex items-center space-x-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'approval' ? 'bg-primary-600 text-white' : 'bg-green-600 text-white'
              }`}>
                1
              </div>
              <span className={step === 'approval' ? 'text-primary-600 font-medium' : 'text-green-600'}>
                Approve NFT
              </span>
              <div className="w-8 h-0.5 bg-gray-300"></div>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'trade' ? 'bg-primary-600 text-white' : 'bg-gray-300 text-gray-500'
              }`}>
                2
              </div>
              <span className={step === 'trade' ? 'text-primary-600 font-medium' : 'text-gray-500'}>
                Create Trade
              </span>
            </div>
          </div>

          {/* Approval Step */}
          {step === 'approval' && (
            <div className="space-y-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">Step 1: Approve NFT Transfer</h3>
                <p className="text-sm text-blue-800 mb-4">
                  Before creating a trade, you need to approve the BarterExchange contract to transfer your NFT when a trade is executed.
                </p>
                <button
                  type="button"
                  onClick={handleApproval}
                  className="btn-primary w-full flex items-center justify-center"
                  disabled={isLoading}
                >
                  {isApproving ? (
                    <>
                      <div className="loading-spinner mr-2"></div>
                      Approving...
                    </>
                  ) : (
                    'Approve NFT Transfer'
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Trade Creation Form */}
          {step === 'trade' && (
            <div className="space-y-4">
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Asset Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    What do you want in return?
                  </label>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="assetType"
                        value={AssetType.ERC721}
                        checked={requestedAssetType === AssetType.ERC721}
                        onChange={(e) => setRequestedAssetType(Number(e.target.value) as AssetType)}
                        className="mr-2"
                      />
                      <span className="text-sm">Another NFT (ERC721)</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="assetType"
                        value={AssetType.ERC20}
                        checked={requestedAssetType === AssetType.ERC20}
                        onChange={(e) => setRequestedAssetType(Number(e.target.value) as AssetType)}
                        className="mr-2"
                      />
                      <span className="text-sm">Tokens (ERC20)</span>
                    </label>
                  </div>
                </div>

                {/* Contract Address */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {requestedAssetType === AssetType.ERC721 ? 'NFT Contract Address' : 'Token Contract Address'}
                  </label>
                  <input
                    type="text"
                    value={requestedContract}
                    onChange={(e) => setRequestedContract(e.target.value)}
                    placeholder="0x..."
                    className="input-field w-full"
                    required
                  />
                </div>

                {/* Token ID or Amount */}
                {requestedAssetType === AssetType.ERC721 ? (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Token ID
                    </label>
                    <input
                      type="text"
                      value={requestedTokenId}
                      onChange={(e) => setRequestedTokenId(e.target.value)}
                      placeholder="1"
                      className="input-field w-full"
                      required
                    />
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Amount (in ETH)
                    </label>
                    <input
                      type="text"
                      value={requestedAmount}
                      onChange={(e) => setRequestedAmount(e.target.value)}
                      placeholder="1.0"
                      className="input-field w-full"
                      required
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Enter the amount in ETH (e.g., 1.5 for 1.5 ETH)
                    </p>
                  </div>
                )}

                {/* Buttons */}
                <div className="flex space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={onClose}
                    className="btn-secondary flex-1"
                    disabled={isLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn-primary flex-1 flex items-center justify-center"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <div className="loading-spinner mr-2"></div>
                        Creating...
                      </>
                    ) : (
                      'Create Trade'
                    )}
                  </button>
                </div>
              </form>

              {/* Helper Text */}
              <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
                <p className="text-xs text-yellow-800">
                  <strong>Note:</strong> The trade will remain open until someone accepts it or you cancel it.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CreateTradeModal 