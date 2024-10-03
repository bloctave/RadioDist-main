// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;

interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

contract USDTDistributor {
    address public owner;
    IERC20 public usdtToken;

    event Distribution(address indexed sender, address indexed recipient, uint256 amount);

    constructor(address _usdtToken) {
        require(_usdtToken != address(0), "USDT token address cannot be zero.");
        owner = msg.sender; // Set owner to the address deploying the contract
        usdtToken = IERC20(_usdtToken); // USDT token contract address
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can execute this function");
        _;
    }

    // Function to distribute USDT with proper validation
    function distribute(address recipient, uint256 amountInUSDT) public onlyOwner {
        require(recipient != address(0), "Recipient address cannot be zero.");
        uint256 amountWithDecimals = amountInUSDT * 1e6; // Convert USDT amount to include six decimal places
        require(usdtToken.transferFrom(owner, recipient, amountWithDecimals), "Transfer failed");
        emit Distribution(owner, recipient, amountWithDecimals);
    }

    // Function to handle decimal USDT amounts
    function distributeDecimal(address recipient, uint256 wholePart, uint256 decimalPart) public onlyOwner {
        require(recipient != address(0), "Recipient address cannot be zero.");
        require(decimalPart < 1e6, "Decimal part should be less than 1e6 for six decimal precision");
        uint256 amountInUSDT = wholePart * 1e6 + decimalPart;
        require(usdtToken.transferFrom(owner, recipient, amountInUSDT), "Transfer failed");
        emit Distribution(owner, recipient, amountInUSDT);
    }
}
