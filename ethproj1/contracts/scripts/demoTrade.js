// SPDX-License-Identifier: MIT
// scripts/demoTrade.js

/*
  Demo Script – Free Trade & Exchange
  ----------------------------------
  1. Deploys BarterExchange, MockNFT, MockToken
  2. Mints two NFTs – one to Alice, one to Bob
  3. Alice lists her NFT for Bob’s NFT (free trade)
  4. Bob accepts and executes trade

  Run:
    npx hardhat run scripts/demoTrade.js --network hardhat
*/

const hre = require("hardhat")

async function main () {
  const [deployer, alice, bob] = await hre.ethers.getSigners()

  console.log("Deployer:", deployer.address)
  console.log("Alice:", alice.address)
  console.log("Bob:", bob.address)

  // 1. Deploy BarterExchange
  const BarterExchange = await hre.ethers.getContractFactory("BarterExchange")
  const barter = await BarterExchange.deploy()
  await barter.waitForDeployment()
  console.log("BarterExchange deployed:", await barter.getAddress())

  // 2. Deploy MockNFT & mint NFTs
  const MockNFT = await hre.ethers.getContractFactory("MockNFT")
  const nft = await MockNFT.deploy("Demo NFT", "DNFT")
  await nft.waitForDeployment()
  console.log("MockNFT deployed:", await nft.getAddress())

  // Mint token #1 to Alice, #2 to Bob
  await nft.connect(deployer).mint(alice.address, "ipfs://alice-nft")
  await nft.connect(deployer).mint(bob.address, "ipfs://bob-nft")
  console.log("Minted token 1 to Alice & token 2 to Bob")

  // 3. Alice approves and lists trade (wants Bob's token 2)
  await nft.connect(alice).approve(await barter.getAddress(), 1)
  const txList = await barter.connect(alice).createTrade(
    await nft.getAddress(),
    1,                      // offered tokenId
    await nft.getAddress(), // requested contract (same NFT contract)
    2,                      // requested tokenId (Bob's)
    0                       // AssetType.ERC721
  )
  const receiptList = await txList.wait()
  const tradeId = receiptList.logs.find(l => l.eventName === "TradeListed").args.tradeId
  console.log(`Trade #${tradeId} listed by Alice: token 1 -> token 2`)

  // 4. Bob approves his NFT and executes trade
  await nft.connect(bob).approve(await barter.getAddress(), 2)
  const txExec = await barter.connect(bob).executeTrade(tradeId)
  await txExec.wait()
  console.log("Trade executed by Bob!")

  // Verify ownership has swapped
  const owner1 = await nft.ownerOf(1)
  const owner2 = await nft.ownerOf(2)
  console.log("Owner of token 1:", owner1)
  console.log("Owner of token 2:", owner2)
}

main()
  .then(() => process.exit(0))
  .catch(err => {
    console.error(err)
    process.exit(1)
  }) 