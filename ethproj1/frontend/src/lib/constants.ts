// Common constants used throughout the application

// Ethereum zero address
export const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000' as const

// Common token decimals
export const ETH_DECIMALS = 18
export const USDC_DECIMALS = 6
export const USDT_DECIMALS = 6

// Network chain IDs
export const CHAIN_IDS = {
  MAINNET: 1,
  SEPOLIA: 11155111,
  HARDHAT: 31337,
} as const

// Default gas limits
export const GAS_LIMITS = {
  CREATE_TRADE: 300000,
  EXECUTE_TRADE: 500000,
  CANCEL_TRADE: 100000,
} as const

// Time constants
export const TIME_CONSTANTS = {
  BLOCK_TIME: 12, // seconds
  DAY_IN_SECONDS: 86400,
  WEEK_IN_SECONDS: 604800,
} as const 