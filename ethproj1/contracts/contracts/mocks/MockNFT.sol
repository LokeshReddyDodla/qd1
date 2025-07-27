// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MockNFT
 * @dev A mock Financial NFT contract for testing purposes
 */
contract MockNFT is ERC721, Ownable {
    uint256 private _nextTokenId;
    mapping(uint256 => string) private _tokenURIs;

    constructor(string memory name, string memory symbol) ERC721(name, symbol) Ownable(msg.sender) {
        _nextTokenId = 1;
    }

    /**
     * @dev Mint a new NFT to the specified address
     */
    function mint(address to, string memory _tokenURI) external onlyOwner returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _mint(to, tokenId);
        _setTokenURI(tokenId, _tokenURI);
        return tokenId;
    }

    /**
     * @dev Mint NFT to caller (for testing)
     */
    function mintToSelf(string memory _tokenURI) external returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _mint(msg.sender, tokenId);
        _setTokenURI(tokenId, _tokenURI);
        return tokenId;
    }

    /**
     * @dev Set the token URI for a specific token
     */
    function _setTokenURI(uint256 tokenId, string memory _tokenURI) internal {
        _requireOwned(tokenId);
        _tokenURIs[tokenId] = _tokenURI;
    }

    /**
     * @dev Get the token URI for a specific token
     */
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        _requireOwned(tokenId);
        return _tokenURIs[tokenId];
    }

    /**
     * @dev Get the next token ID
     */
    function getNextTokenId() external view returns (uint256) {
        return _nextTokenId;
    }
} 