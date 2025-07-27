# P2P Financial NFT Barter Exchange

A decentralized application (dApp) for peer-to-peer trading of Financial NFTs with real-time net value calculations and atomic swaps.

## Project Overview

This platform is designed for experienced DeFi users to trade complex financial instruments represented as NFTs (like Uniswap V3 LP positions, Aave yield tokens, etc.) in a specialized, data-rich environment.

### Key Features

- **Portfolio Dashboard**: Scans wallet for Financial NFTs with live net value calculations
- **Atomic Swaps**: Non-custodial trading via smart contracts  
- **Real-time Valuations**: Client-side calculation of underlying asset values
- **Tool-first Design**: Built for power users who need detailed financial data

## Architecture

```
ethproj1/
├── contracts/          # Smart contracts (Hardhat)
├── frontend/           # Next.js web application
└── subgraph/           # TheGraph indexing (planned)
```

## Smart Contracts

### BarterExchange Contract

The core contract facilitates atomic swaps between:
- NFT ↔ NFT trades
- NFT ↔ ERC20 token trades

**Key Functions:**
- `createTrade()` - List an NFT for trade
- `executeTrade()` - Accept and execute a trade
- `cancelTrade()` - Cancel your own trade listing

**Security Features:**
- Non-custodial (never holds user assets)
- Approval-based transfers only
- Comprehensive validation checks
- Reentrancy protection

### Test Coverage

✅ 25 passing tests covering:
- Trade creation and validation
- Atomic swap execution
- Cancellation logic
- Security edge cases
- View functions

## Frontend Application

### Tech Stack

- **Framework**: Next.js 14 with App Router
- **Wallet Integration**: RainbowKit + Wagmi
- **Styling**: TailwindCSS
- **Blockchain**: Ethers.js / Viem
- **Type Safety**: TypeScript

### Components

1. **Portfolio Dashboard** - Main user interface showing owned Financial NFTs
2. **NFT Cards** - Display individual NFTs with live valuations
3. **Trade Creation Modal** - Interface for creating new trade listings
4. **Marketplace View** - Browse available trades (planned)

### Live Net Value Calculation (Planned)

The frontend will calculate real-time USD values by:
1. Reading NFT composition from protocol contracts (e.g., Uniswap NonfungiblePositionManager)
2. Fetching token prices from Chainlink Data Feeds
3. Computing spot prices from DEX liquidity pools
4. Displaying verifiable calculations to users

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ethproj1
   ```

2. **Install dependencies**
   ```bash
   npm install
   cd contracts && npm install
   cd ../frontend && npm install
   ```

3. **Set up environment files**
   ```bash
   # Copy environment templates
   cp contracts/env.example contracts/.env
   cp frontend/env.example frontend/.env.local
   
   # Edit the files with your API keys
   ```

4. **Compile and test smart contracts**
   ```bash
   cd contracts
   npm run compile
   npm run test
   ```

5. **Start the frontend development server**
   ```bash
   cd frontend
   npm run dev
   ```

6. **Visit the application**
   Open [http://localhost:3000](http://localhost:3000) in your browser

### Configuration

#### Contracts Environment (contracts/.env)
```bash
SEPOLIA_URL=https://sepolia.infura.io/v3/YOUR_INFURA_API_KEY
PRIVATE_KEY=your_private_key_here
ETHERSCAN_API_KEY=your_etherscan_api_key_here
```

#### Frontend Environment (frontend/.env.local)
```bash
NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID=your_walletconnect_project_id
NEXT_PUBLIC_ALCHEMY_ID=your_alchemy_api_key
```

## Deployment

### Testnet Deployment (Sepolia)

1. **Deploy contracts**
   ```bash
   cd contracts
   npm run deploy:sepolia
   ```

2. **Update frontend configuration**
   ```bash
   # Copy contract addresses from contracts/deployments/sepolia.json
   # to frontend/.env.local
   ```

3. **Build and deploy frontend**
   ```bash
   cd frontend
   npm run build
   ```

## Development Roadmap

### Phase 1: Smart Contract Development ✅
- [x] BarterExchange contract
- [x] Mock contracts for testing
- [x] Comprehensive test suite
- [x] Deployment scripts

### Phase 2: Frontend Development ✅ (Basic)
- [x] Next.js setup with RainbowKit
- [x] Portfolio dashboard
- [x] Trade creation modal
- [x] Basic wallet integration
- [ ] Live net value calculation
- [ ] Contract integration

### Phase 3: Data Indexing (Planned)
- [ ] TheGraph subgraph development
- [ ] Event indexing for trade listings
- [ ] GraphQL API integration

### Phase 4: Advanced Features (Planned)
- [ ] Marketplace view
- [ ] Trade history
- [ ] Advanced filtering/sorting
- [ ] Price alerts
- [ ] Portfolio analytics

## Testing

### Smart Contracts
```bash
cd contracts
npm run test
```

### Frontend
```bash
cd frontend
npm run lint
npm run build
```

## Security Considerations

- **Non-custodial Design**: Contract never holds user assets
- **Approval-based**: Uses ERC721/ERC20 approval patterns
- **Validation**: Extensive ownership and approval checks
- **Testing**: Comprehensive test coverage including edge cases
- **Static Analysis**: Planned Slither integration

## Contributing

This is currently a personal project. For suggestions or issues, please open an issue in the repository.

## License

MIT License - see LICENSE file for details.

## Target Audience

**"Adi, the DeFi Strategist"**: An experienced DeFi user who:
- Manages diverse portfolios of yield-bearing assets
- Values data accuracy and verifiability
- Needs tools for precise portfolio rebalancing
- Comfortable with complex protocols
- Task-oriented and efficiency-focused

## Design Principles

1. **Tool First, Marketplace Second**: Personal dashboard is the primary entry point
2. **Data Density**: Rich financial information prominently displayed  
3. **Desktop First**: Optimized for serious trading workflows
4. **Verifiable Calculations**: All valuations show underlying data
5. **Power User Focus**: No hand-holding, built for experts 