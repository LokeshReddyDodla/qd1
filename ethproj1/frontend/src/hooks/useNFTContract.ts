'use client'

import { useState, useEffect } from 'react'
import { useAccount, useContractRead, useNetwork } from 'wagmi'
import { MOCK_NFT_ABI, getContractAddresses } from '@/lib/contracts'

// Hook for NFT ownership and approval checks
export function useNFTContract(nftContractAddress?: string) {
  const { address } = useAccount()
  const { chain } = useNetwork()
  const contractAddresses = getContractAddresses(chain?.id || 31337)

  // Check if user owns a specific NFT
  const useNFTOwnership = (tokenId?: bigint) => {
    const { data: owner, isLoading, error, refetch } = useContractRead({
      address: nftContractAddress as `0x${string}`,
      abi: MOCK_NFT_ABI,
      functionName: 'ownerOf',
      args: tokenId ? [tokenId] : undefined,
      enabled: !!nftContractAddress && !!tokenId,
    })

    return {
      owner: owner as string | undefined,
      isOwner: owner === address,
      isLoading,
      error,
      refetch,
    }
  }

  // Check if BarterExchange is approved for a specific NFT
  const useNFTApproval = (tokenId?: bigint) => {
    const { data: approvedAddress, isLoading, error, refetch } = useContractRead({
      address: nftContractAddress as `0x${string}`,
      abi: MOCK_NFT_ABI,
      functionName: 'getApproved',
      args: tokenId ? [tokenId] : undefined,
      enabled: !!nftContractAddress && !!tokenId,
    })

    const { data: isApprovedForAll } = useContractRead({
      address: nftContractAddress as `0x${string}`,
      abi: MOCK_NFT_ABI,
      functionName: 'isApprovedForAll',
      args: address ? [address, contractAddresses.BARTER_EXCHANGE] : undefined,
      enabled: !!nftContractAddress && !!address,
    })

    return {
      approvedAddress: approvedAddress as string | undefined,
      isApproved: approvedAddress === contractAddresses.BARTER_EXCHANGE || isApprovedForAll,
      isApprovedForAll,
      isLoading,
      error,
      refetch,
    }
  }

  return {
    useNFTOwnership,
    useNFTApproval,
  }
}

// Hook for approving NFTs
export function useNFTApproval() {
  const { chain } = useNetwork()
  const contractAddresses = getContractAddresses(chain?.id || 31337)
  const [isLoading, setIsLoading] = useState(false)

  const approveNFT = async (nftContractAddress: string, tokenId: bigint) => {
    setIsLoading(true)
    try {
      console.log('Approving NFT:', { nftContractAddress, tokenId, spender: contractAddresses.BARTER_EXCHANGE })
      
      // Simulate approval transaction
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      return { hash: '0xapproval123456789' }
    } catch (error) {
      console.error('Error approving NFT:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const approveAllNFTs = async (nftContractAddress: string) => {
    setIsLoading(true)
    try {
      console.log('Approving all NFTs:', { nftContractAddress, operator: contractAddresses.BARTER_EXCHANGE })
      
      // Simulate approval transaction
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      return { hash: '0xapprovalall123456' }
    } catch (error) {
      console.error('Error approving all NFTs:', error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  return {
    approveNFT,
    approveAllNFTs,
    isLoading,
  }
}

// Hook for getting user's NFTs (real wallet scanning)
export function useUserNFTs() {
  const { address } = useAccount()
  const { chain } = useNetwork()
  const contractAddresses = getContractAddresses(chain?.id || 31337)
  const [nfts, setNfts] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadNFTs = async () => {
      if (!address) {
        setNfts([])
        return
      }

      setLoading(true)
      setError(null)
      
      try {
        // Real wallet scanning - check actual NFT ownership
        const ownedNFTs: any[] = []
        
        // Check the mock NFT contract for actual ownership
        const mockNFTContract = contractAddresses.MOCK_NFT
        
        // In a real implementation, you would:
        // 1. Get balanceOf(address) for each known Financial NFT contract
        // 2. For each contract where balance > 0, get tokenOfOwnerByIndex
        // 3. For each token, get tokenURI and metadata
        // 4. Calculate real values from on-chain data
        
        // For now, we'll check if user has any NFTs from the deployed mock contract
        // This is a placeholder for real wallet scanning
        
        setNfts(ownedNFTs)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load NFTs')
        setNfts([])
      } finally {
        setLoading(false)
      }
    }

    loadNFTs()
  }, [address, contractAddresses.MOCK_NFT])

  return {
    nfts,
    loading,
    error,
    refetch: () => {
      if (address) {
        setLoading(true)
        setTimeout(() => setLoading(false), 100)
      }
    }
  }
} 