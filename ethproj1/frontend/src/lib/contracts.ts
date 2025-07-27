import BarterExchangeArtifact from './BarterExchange.json'
import MockNFTArtifact from './MockNFT.json'
import MockTokenArtifact from './MockToken.json'

// Contract ABIs
export const BARTER_EXCHANGE_ABI = BarterExchangeArtifact.abi
export const MOCK_NFT_ABI = MockNFTArtifact.abi
export const MOCK_TOKEN_ABI = MockTokenArtifact.abi

// Contract addresses - these will be updated based on deployment
export const CONTRACT_ADDRESSES = {
  // Hardhat local development
  31337: {
    BARTER_EXCHANGE: '0x5FbDB2315678afecb367f032d93F642f64180aa3',
    MOCK_NFT: '0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512',
    MOCK_TOKEN: '0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0',
  },
  // Sepolia testnet
  11155111: {
    BARTER_EXCHANGE: process.env.NEXT_PUBLIC_BARTER_CONTRACT_ADDRESS || '',
    MOCK_NFT: process.env.NEXT_PUBLIC_MOCK_NFT_ADDRESS || '',
    MOCK_TOKEN: process.env.NEXT_PUBLIC_MOCK_TOKEN_ADDRESS || '',
  },
} as const

// Asset types enum to match contract
export enum AssetType {
  ERC721 = 0,
  ERC20 = 1
}

// Trade status enum to match contract
export enum TradeStatus {
  Open = 0,
  Closed = 1,
  Cancelled = 2
}

// Type definitions
export interface Trade {
  tradeId: bigint
  lister: string
  offeredNftContract: string
  offeredNftId: bigint
  requestedAssetContract: string
  requestedAssetIdOrAmount: bigint
  requestedAssetType: AssetType
  status: TradeStatus
  createdAt: bigint
}

export interface CreateTradeParams {
  offeredNftContract: string
  offeredNftId: bigint
  requestedAssetContract: string
  requestedAssetIdOrAmount: bigint
  requestedAssetType: AssetType
}

// Helper function to get contract addresses for current chain
export function getContractAddresses(chainId: number) {
  return CONTRACT_ADDRESSES[chainId as keyof typeof CONTRACT_ADDRESSES] || CONTRACT_ADDRESSES[31337]
} 