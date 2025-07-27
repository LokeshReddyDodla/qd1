// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title BarterExchange
 * @dev A peer-to-peer exchange for trading Financial NFTs and ERC20 tokens
 * @notice This contract facilitates atomic swaps without holding user assets
 */
contract BarterExchange is ReentrancyGuard, Ownable {
    enum Status {
        Open,
        Closed,
        Cancelled
    }

    enum AssetType {
        ERC721,
        ERC20
    }

    struct Trade {
        uint256 tradeId;
        address lister;
        address offeredNftContract;
        uint256 offeredNftId;
        address requestedAssetContract;
        uint256 requestedAssetIdOrAmount;
        AssetType requestedAssetType;
        Status status;
        uint256 createdAt;
    }

    uint256 private _nextTradeId;
    mapping(uint256 => Trade) public trades;
    
    // Events
    event TradeListed(
        uint256 indexed tradeId,
        address indexed lister,
        address indexed offeredNftContract,
        uint256 offeredNftId,
        address requestedAssetContract,
        uint256 requestedAssetIdOrAmount,
        AssetType requestedAssetType
    );

    event TradeExecuted(
        uint256 indexed tradeId,
        address indexed lister,
        address indexed acceptor,
        address offeredNftContract,
        uint256 offeredNftId,
        address requestedAssetContract,
        uint256 requestedAssetIdOrAmount
    );

    event TradeCancelled(
        uint256 indexed tradeId,
        address indexed lister
    );

    constructor() Ownable(msg.sender) {
        _nextTradeId = 1;
    }

    /**
     * @dev Create a new trade listing
     * @param offeredNftContract The contract address of the NFT being offered
     * @param offeredNftId The token ID of the NFT being offered
     * @param requestedAssetContract The contract address of the requested asset
     * @param requestedAssetIdOrAmount The token ID (for NFT) or amount (for ERC20)
     * @param requestedAssetType Whether the requested asset is ERC721 or ERC20
     */
    function createTrade(
        address offeredNftContract,
        uint256 offeredNftId,
        address requestedAssetContract,
        uint256 requestedAssetIdOrAmount,
        AssetType requestedAssetType
    ) external nonReentrant returns (uint256) {
        require(offeredNftContract != address(0), "Invalid NFT contract");
        require(requestedAssetContract != address(0), "Invalid requested asset contract");
        
        // Verify the caller owns the offered NFT
        IERC721 nftContract = IERC721(offeredNftContract);
        require(nftContract.ownerOf(offeredNftId) == msg.sender, "Not owner of offered NFT");
        
        // Verify this contract is approved to transfer the NFT
        require(
            nftContract.isApprovedForAll(msg.sender, address(this)) ||
            nftContract.getApproved(offeredNftId) == address(this),
            "Contract not approved to transfer NFT"
        );

        uint256 tradeId = _nextTradeId++;
        
        trades[tradeId] = Trade({
            tradeId: tradeId,
            lister: msg.sender,
            offeredNftContract: offeredNftContract,
            offeredNftId: offeredNftId,
            requestedAssetContract: requestedAssetContract,
            requestedAssetIdOrAmount: requestedAssetIdOrAmount,
            requestedAssetType: requestedAssetType,
            status: Status.Open,
            createdAt: block.timestamp
        });

        emit TradeListed(
            tradeId,
            msg.sender,
            offeredNftContract,
            offeredNftId,
            requestedAssetContract,
            requestedAssetIdOrAmount,
            requestedAssetType
        );

        return tradeId;
    }

    /**
     * @dev Execute a trade by accepting it
     * @param tradeId The ID of the trade to execute
     */
    function executeTrade(uint256 tradeId) external nonReentrant {
        Trade storage trade = trades[tradeId];
        
        require(trade.tradeId != 0, "Trade does not exist");
        require(trade.status == Status.Open, "Trade is not open");
        require(trade.lister != msg.sender, "Cannot accept your own trade");

        // Verify lister still owns the offered NFT
        IERC721 offeredNft = IERC721(trade.offeredNftContract);
        require(offeredNft.ownerOf(trade.offeredNftId) == trade.lister, "Lister no longer owns offered NFT");

        // Verify contract is still approved to transfer the offered NFT
        require(
            offeredNft.isApprovedForAll(trade.lister, address(this)) ||
            offeredNft.getApproved(trade.offeredNftId) == address(this),
            "Contract no longer approved for offered NFT"
        );

        if (trade.requestedAssetType == AssetType.ERC721) {
            // Handle NFT for NFT trade
            IERC721 requestedNft = IERC721(trade.requestedAssetContract);
            
            require(requestedNft.ownerOf(trade.requestedAssetIdOrAmount) == msg.sender, "Not owner of requested NFT");
            require(
                requestedNft.isApprovedForAll(msg.sender, address(this)) ||
                requestedNft.getApproved(trade.requestedAssetIdOrAmount) == address(this),
                "Contract not approved for requested NFT"
            );

            // Execute atomic swap
            offeredNft.safeTransferFrom(trade.lister, msg.sender, trade.offeredNftId);
            requestedNft.safeTransferFrom(msg.sender, trade.lister, trade.requestedAssetIdOrAmount);
        } else {
            // Handle NFT for ERC20 trade
            IERC20 requestedToken = IERC20(trade.requestedAssetContract);
            
            require(requestedToken.balanceOf(msg.sender) >= trade.requestedAssetIdOrAmount, "Insufficient token balance");
            require(requestedToken.allowance(msg.sender, address(this)) >= trade.requestedAssetIdOrAmount, "Insufficient token allowance");

            // Execute atomic swap
            offeredNft.safeTransferFrom(trade.lister, msg.sender, trade.offeredNftId);
            requestedToken.transferFrom(msg.sender, trade.lister, trade.requestedAssetIdOrAmount);
        }

        // Mark trade as closed
        trade.status = Status.Closed;

        emit TradeExecuted(
            tradeId,
            trade.lister,
            msg.sender,
            trade.offeredNftContract,
            trade.offeredNftId,
            trade.requestedAssetContract,
            trade.requestedAssetIdOrAmount
        );
    }

    /**
     * @dev Cancel an open trade
     * @param tradeId The ID of the trade to cancel
     */
    function cancelTrade(uint256 tradeId) external {
        Trade storage trade = trades[tradeId];
        
        require(trade.tradeId != 0, "Trade does not exist");
        require(trade.lister == msg.sender, "Only lister can cancel trade");
        require(trade.status == Status.Open, "Trade is not open");

        trade.status = Status.Cancelled;

        emit TradeCancelled(tradeId, msg.sender);
    }

    /**
     * @dev Get trade details
     * @param tradeId The ID of the trade
     */
    function getTrade(uint256 tradeId) external view returns (Trade memory) {
        require(trades[tradeId].tradeId != 0, "Trade does not exist");
        return trades[tradeId];
    }

    /**
     * @dev Get the next trade ID
     */
    function getNextTradeId() external view returns (uint256) {
        return _nextTradeId;
    }

    /**
     * @dev Get all trades by a specific lister
     * @param lister The address of the lister
     */
    function getTradesByLister(address lister) external view returns (uint256[] memory) {
        uint256[] memory result = new uint256[](_nextTradeId - 1);
        uint256 count = 0;
        
        for (uint256 i = 1; i < _nextTradeId; i++) {
            if (trades[i].lister == lister) {
                result[count] = i;
                count++;
            }
        }
        
        // Resize array to actual count
        uint256[] memory finalResult = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            finalResult[i] = result[i];
        }
        
        return finalResult;
    }

    /**
     * @dev Emergency function to pause contract (only owner)
     */
    function pause() external onlyOwner {
        // Implementation would add pausable functionality if needed
        // For now, this is a placeholder for future security enhancements
    }
} 