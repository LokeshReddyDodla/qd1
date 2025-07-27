const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Starting deployment...");

  // Get the contract factory
  const BarterExchange = await hre.ethers.getContractFactory("BarterExchange");

  // Deploy the contract
  console.log("Deploying BarterExchange...");
  const barterExchange = await BarterExchange.deploy();
  
  await barterExchange.waitForDeployment();
  const barterExchangeAddress = await barterExchange.getAddress();

  console.log(`BarterExchange deployed to: ${barterExchangeAddress}`);

  // Save deployment information
  const deploymentInfo = {
    contractAddress: barterExchangeAddress,
    network: hre.network.name,
    chainId: hre.network.config.chainId,
    deployedAt: new Date().toISOString(),
    contractName: "BarterExchange"
  };

  // Create deployments directory if it doesn't exist
  const deploymentsDir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  // Save deployment info to file
  const deploymentFile = path.join(deploymentsDir, `${hre.network.name}.json`);
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

  console.log(`Deployment info saved to: ${deploymentFile}`);

  // If on a public network, verify the contract
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("Waiting for block confirmations...");
    await barterExchange.deploymentTransaction().wait(6);

    console.log("Verifying contract...");
    try {
      await hre.run("verify:verify", {
        address: barterExchangeAddress,
        constructorArguments: [],
      });
      console.log("Contract verified!");
    } catch (error) {
      console.log("Verification failed:", error.message);
    }
  }

  // Deploy mock contracts if on testnet for testing
  if (hre.network.name === "sepolia" || hre.network.name === "hardhat") {
    console.log("\nDeploying mock contracts for testing...");
    
    const MockNFT = await hre.ethers.getContractFactory("MockNFT");
    const MockToken = await hre.ethers.getContractFactory("MockToken");

    const mockNFT = await MockNFT.deploy("Test Financial NFT", "TFNFT");
    await mockNFT.waitForDeployment();
    const mockNFTAddress = await mockNFT.getAddress();

    const mockToken = await MockToken.deploy("Test Token", "TEST", 18, 1000000);
    await mockToken.waitForDeployment();
    const mockTokenAddress = await mockToken.getAddress();

    console.log(`MockNFT deployed to: ${mockNFTAddress}`);
    console.log(`MockToken deployed to: ${mockTokenAddress}`);

    // Update deployment info with mock contracts
    deploymentInfo.mockContracts = {
      mockNFT: mockNFTAddress,
      mockToken: mockTokenAddress
    };

    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  }

  console.log("\nDeployment completed!");
  return deploymentInfo;
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 