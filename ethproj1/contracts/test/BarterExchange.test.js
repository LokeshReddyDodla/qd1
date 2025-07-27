const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("BarterExchange", function () {
  let barterExchange;
  let mockNFT1, mockNFT2;
  let mockToken;
  let owner, user1, user2, user3;

  const AssetType = {
    ERC721: 0,
    ERC20: 1
  };

  const Status = {
    Open: 0,
    Closed: 1,
    Cancelled: 2
  };

  beforeEach(async function () {
    [owner, user1, user2, user3] = await ethers.getSigners();

    // Deploy BarterExchange
    const BarterExchange = await ethers.getContractFactory("BarterExchange");
    barterExchange = await BarterExchange.deploy();

    // Deploy Mock NFT contracts
    const MockNFT = await ethers.getContractFactory("MockNFT");
    mockNFT1 = await MockNFT.deploy("Financial NFT 1", "FNFT1");
    mockNFT2 = await MockNFT.deploy("Financial NFT 2", "FNFT2");

    // Deploy Mock Token
    const MockToken = await ethers.getContractFactory("MockToken");
    mockToken = await MockToken.deploy("Test Token", "TEST", 18, 1000000);

    // Mint some NFTs for testing
    // mockNFT1: user1 gets token 1, user2 gets token 2
    await mockNFT1.connect(user1).mintToSelf("https://example.com/1");
    await mockNFT1.connect(user2).mintToSelf("https://example.com/2");
    
    // mockNFT2: user1 gets token 1, user2 gets token 2  
    await mockNFT2.connect(user1).mintToSelf("https://example.com/3");
    await mockNFT2.connect(user2).mintToSelf("https://example.com/4");

    // Distribute tokens
    await mockToken.transfer(user1.address, ethers.parseEther("1000"));
    await mockToken.transfer(user2.address, ethers.parseEther("1000"));
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await barterExchange.owner()).to.equal(owner.address);
    });

    it("Should initialize nextTradeId to 1", async function () {
      expect(await barterExchange.getNextTradeId()).to.equal(1);
    });
  });

  describe("Trade Creation", function () {
    it("Should create a trade for NFT to NFT swap", async function () {
      // User1 approves the barter contract to transfer their NFT
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);

      const tx = await barterExchange.connect(user1).createTrade(
        mockNFT1.target,
        1,
        mockNFT2.target,
        2,
        AssetType.ERC721
      );

      await expect(tx)
        .to.emit(barterExchange, "TradeListed")
        .withArgs(1, user1.address, mockNFT1.target, 1, mockNFT2.target, 2, AssetType.ERC721);

      const trade = await barterExchange.getTrade(1);
      expect(trade.tradeId).to.equal(1);
      expect(trade.lister).to.equal(user1.address);
      expect(trade.status).to.equal(Status.Open);
    });

    it("Should create a trade for NFT to ERC20 swap", async function () {
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);

      const requestedAmount = ethers.parseEther("100");
      await barterExchange.connect(user1).createTrade(
        mockNFT1.target,
        1,
        mockToken.target,
        requestedAmount,
        AssetType.ERC20
      );

      const trade = await barterExchange.getTrade(1);
      expect(trade.requestedAssetIdOrAmount).to.equal(requestedAmount);
      expect(trade.requestedAssetType).to.equal(AssetType.ERC20);
    });

    it("Should fail if caller doesn't own the NFT", async function () {
      await expect(
        barterExchange.connect(user2).createTrade(
          mockNFT1.target,
          1, // This NFT belongs to user1
          mockNFT2.target,
          1,
          AssetType.ERC721
        )
      ).to.be.revertedWith("Not owner of offered NFT");
    });

    it("Should fail if contract is not approved", async function () {
      // Don't approve the contract
      await expect(
        barterExchange.connect(user1).createTrade(
          mockNFT1.target,
          1,
          mockNFT2.target,
          1,
          AssetType.ERC721
        )
      ).to.be.revertedWith("Contract not approved to transfer NFT");
    });

    it("Should fail with zero address contracts", async function () {
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);

      await expect(
        barterExchange.connect(user1).createTrade(
          ethers.ZeroAddress,
          1,
          mockNFT2.target,
          1,
          AssetType.ERC721
        )
      ).to.be.revertedWith("Invalid NFT contract");

      await expect(
        barterExchange.connect(user1).createTrade(
          mockNFT1.target,
          1,
          ethers.ZeroAddress,
          1,
          AssetType.ERC721
        )
      ).to.be.revertedWith("Invalid requested asset contract");
    });
  });

  describe("Trade Execution - NFT to NFT", function () {
    beforeEach(async function () {
      // User1 creates a trade: NFT1 token 1 for NFT2 token 2 (which user2 owns)
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);
      await barterExchange.connect(user1).createTrade(
        mockNFT1.target,
        1,
        mockNFT2.target,
        2,
        AssetType.ERC721
      );
    });

    it("Should execute NFT to NFT trade successfully", async function () {
      // User2 approves their NFT and executes the trade
      await mockNFT2.connect(user2).approve(barterExchange.target, 2);

      const tx = await barterExchange.connect(user2).executeTrade(1);

      await expect(tx)
        .to.emit(barterExchange, "TradeExecuted")
        .withArgs(1, user1.address, user2.address, mockNFT1.target, 1, mockNFT2.target, 2);

      // Check ownership transfers
      expect(await mockNFT1.ownerOf(1)).to.equal(user2.address);
      expect(await mockNFT2.ownerOf(2)).to.equal(user1.address);

      // Check trade status
      const trade = await barterExchange.getTrade(1);
      expect(trade.status).to.equal(Status.Closed);
    });

    it("Should fail if acceptor doesn't own the requested NFT", async function () {
      await expect(
        barterExchange.connect(user3).executeTrade(1)
      ).to.be.revertedWith("Not owner of requested NFT");
    });

    it("Should fail if acceptor hasn't approved the contract", async function () {
      // user2 doesn't approve their NFT token 2
      await expect(
        barterExchange.connect(user2).executeTrade(1)
      ).to.be.revertedWith("Contract not approved for requested NFT");
    });

    it("Should fail if lister tries to accept their own trade", async function () {
      await expect(
        barterExchange.connect(user1).executeTrade(1)
      ).to.be.revertedWith("Cannot accept your own trade");
    });

    it("Should fail if trade doesn't exist", async function () {
      await expect(
        barterExchange.connect(user2).executeTrade(999)
      ).to.be.revertedWith("Trade does not exist");
    });
  });

  describe("Trade Execution - NFT to ERC20", function () {
    beforeEach(async function () {
      // User1 creates a trade: NFT1 token 1 for 100 tokens
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);
      await barterExchange.connect(user1).createTrade(
        mockNFT1.target,
        1,
        mockToken.target,
        ethers.parseEther("100"),
        AssetType.ERC20
      );
    });

    it("Should execute NFT to ERC20 trade successfully", async function () {
      // User2 approves tokens and executes the trade
      await mockToken.connect(user2).approve(barterExchange.target, ethers.parseEther("100"));

      const user1BalanceBefore = await mockToken.balanceOf(user1.address);
      const user2BalanceBefore = await mockToken.balanceOf(user2.address);

      await barterExchange.connect(user2).executeTrade(1);

      // Check ownership transfers
      expect(await mockNFT1.ownerOf(1)).to.equal(user2.address);
      expect(await mockToken.balanceOf(user1.address)).to.equal(user1BalanceBefore + ethers.parseEther("100"));
      expect(await mockToken.balanceOf(user2.address)).to.equal(user2BalanceBefore - ethers.parseEther("100"));
    });

    it("Should fail if acceptor has insufficient token balance", async function () {
      // Transfer away user2's tokens
      await mockToken.connect(user2).transfer(user3.address, ethers.parseEther("1000"));

      await mockToken.connect(user2).approve(barterExchange.target, ethers.parseEther("100"));

      await expect(
        barterExchange.connect(user2).executeTrade(1)
      ).to.be.revertedWith("Insufficient token balance");
    });

    it("Should fail if acceptor hasn't approved enough tokens", async function () {
      await mockToken.connect(user2).approve(barterExchange.target, ethers.parseEther("50")); // Less than required

      await expect(
        barterExchange.connect(user2).executeTrade(1)
      ).to.be.revertedWith("Insufficient token allowance");
    });
  });

  describe("Trade Cancellation", function () {
    beforeEach(async function () {
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);
      await barterExchange.connect(user1).createTrade(
        mockNFT1.target,
        1,
        mockNFT2.target,
        2,
        AssetType.ERC721
      );
    });

    it("Should allow lister to cancel their trade", async function () {
      const tx = await barterExchange.connect(user1).cancelTrade(1);

      await expect(tx)
        .to.emit(barterExchange, "TradeCancelled")
        .withArgs(1, user1.address);

      const trade = await barterExchange.getTrade(1);
      expect(trade.status).to.equal(Status.Cancelled);
    });

    it("Should fail if non-lister tries to cancel", async function () {
      await expect(
        barterExchange.connect(user2).cancelTrade(1)
      ).to.be.revertedWith("Only lister can cancel trade");
    });

    it("Should fail to cancel non-existent trade", async function () {
      await expect(
        barterExchange.connect(user1).cancelTrade(999)
      ).to.be.revertedWith("Trade does not exist");
    });

    it("Should fail to execute cancelled trade", async function () {
      await barterExchange.connect(user1).cancelTrade(1);
      await mockNFT2.connect(user2).approve(barterExchange.target, 2);

      await expect(
        barterExchange.connect(user2).executeTrade(1)
      ).to.be.revertedWith("Trade is not open");
    });
  });

  describe("Edge Cases and Security", function () {
    it("Should fail if lister no longer owns the NFT during execution", async function () {
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);
      await barterExchange.connect(user1).createTrade(
        mockNFT1.target,
        1,
        mockNFT2.target,
        2,
        AssetType.ERC721
      );

      // User1 transfers their NFT away
      await mockNFT1.connect(user1).transferFrom(user1.address, user3.address, 1);

      await mockNFT2.connect(user2).approve(barterExchange.target, 2);

      await expect(
        barterExchange.connect(user2).executeTrade(1)
      ).to.be.revertedWith("Lister no longer owns offered NFT");
    });

    it("Should fail if approval is revoked after trade creation", async function () {
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);
      await barterExchange.connect(user1).createTrade(
        mockNFT1.target,
        1,
        mockNFT2.target,
        2,
        AssetType.ERC721
      );

      // User1 revokes approval
      await mockNFT1.connect(user1).approve(ethers.ZeroAddress, 1);

      await mockNFT2.connect(user2).approve(barterExchange.target, 2);

      await expect(
        barterExchange.connect(user2).executeTrade(1)
      ).to.be.revertedWith("Contract no longer approved for offered NFT");
    });

    it("Should handle multiple trades by same user", async function () {
      // User1 creates multiple trades
      await mockNFT1.connect(user1).mintToSelf("https://example.com/5");
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);
      await mockNFT1.connect(user1).approve(barterExchange.target, 3);

      await barterExchange.connect(user1).createTrade(
        mockNFT1.target, 1, mockNFT2.target, 2, AssetType.ERC721
      );
      await barterExchange.connect(user1).createTrade(
        mockNFT1.target, 3, mockToken.target, ethers.parseEther("50"), AssetType.ERC20
      );

      const trades = await barterExchange.getTradesByLister(user1.address);
      expect(trades.length).to.equal(2);
      expect(trades[0]).to.equal(1);
      expect(trades[1]).to.equal(2);
    });
  });

  describe("View Functions", function () {
    beforeEach(async function () {
      await mockNFT1.connect(user1).approve(barterExchange.target, 1);
      await barterExchange.connect(user1).createTrade(
        mockNFT1.target,
        1,
        mockNFT2.target,
        2,
        AssetType.ERC721
      );
    });

    it("Should return correct trade details", async function () {
      const trade = await barterExchange.getTrade(1);
      expect(trade.tradeId).to.equal(1);
      expect(trade.lister).to.equal(user1.address);
      expect(trade.offeredNftContract).to.equal(mockNFT1.target);
      expect(trade.offeredNftId).to.equal(1);
      expect(trade.requestedAssetContract).to.equal(mockNFT2.target);
      expect(trade.requestedAssetIdOrAmount).to.equal(2);
      expect(trade.requestedAssetType).to.equal(AssetType.ERC721);
      expect(trade.status).to.equal(Status.Open);
      expect(trade.createdAt).to.be.gt(0);
    });

    it("Should increment trade ID correctly", async function () {
      expect(await barterExchange.getNextTradeId()).to.equal(2);
    });

    it("Should return empty array for user with no trades", async function () {
      const trades = await barterExchange.getTradesByLister(user3.address);
      expect(trades.length).to.equal(0);
    });
  });
}); 