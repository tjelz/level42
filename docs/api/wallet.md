# WalletManager API Reference

The `WalletManager` class handles cryptocurrency wallet operations and blockchain interactions for the x402-Agent Framework.

## Class Definition

```python
class WalletManager:
    """
    Manages cryptocurrency wallets and blockchain transactions.
    
    Provides secure wallet operations including balance checking, payments,
    and transaction batching across multiple blockchain networks.
    """
```

## Constructor

### `__init__(private_key, network="base")`

Initialize a new WalletManager instance.

**Parameters:**
- `private_key` (str): Private key for the wallet (64 hex characters with 0x prefix)
- `network` (str, optional): Blockchain network to use. Defaults to "base"

**Supported Networks:**
- `"base"`: Base Network (Layer 2 Ethereum)
- `"solana"`: Solana Network
- `"ethereum"`: Ethereum Mainnet (coming soon)

**Raises:**
- `ValueError`: If private key format is invalid
- `NetworkError`: If network is unsupported or unreachable

**Example:**
```python
from x402_agent.wallet import WalletManager

wallet = WalletManager(
    private_key="0x1234567890abcdef...",
    network="base"
)
```

## Properties

### `address`
The public wallet address derived from the private key.

**Type:** `str`

**Example:**
```python
print(f"Wallet address: {wallet.address}")
# Output: Wallet address: 0xabcd1234...
```

### `network`
The current blockchain network being used.

**Type:** `str`

### `network_provider`
The network provider instance for blockchain operations.

**Type:** `NetworkProvider`

## Methods

### `get_balance()`

Get the current USDC balance in the wallet.

**Returns:**
- `float`: Current balance in USDC

**Raises:**
- `NetworkError`: If unable to connect to blockchain
- `WalletError`: If wallet address is invalid

**Example:**
```python
balance = wallet.get_balance()
print(f"Current balance: ${balance:.2f} USDC")
```

### `get_native_balance()`

Get the current native token balance (ETH, SOL, etc.) for gas fees.

**Returns:**
- `float`: Current native token balance

**Example:**
```python
native_balance = wallet.get_native_balance()
print(f"ETH balance: {native_balance:.6f} ETH")
```

### `make_payment(amount, recipient, memo="")`

Execute a single USDC payment to a recipient address.

**Parameters:**
- `amount` (float): Amount to send in USDC
- `recipient` (str): Recipient wallet address
- `memo` (str, optional): Optional payment memo/description

**Returns:**
- `str`: Transaction hash of the completed payment

**Raises:**
- `InsufficientFundsError`: If wallet balance is too low
- `PaymentError`: If payment processing fails
- `NetworkError`: If blockchain network is unavailable

**Example:**
```python
tx_hash = wallet.make_payment(
    amount=5.0,
    recipient="0xrecipient123...",
    memo="API payment for weather data"
)
print(f"Payment sent: {tx_hash}")
```

### `batch_payments(payments)`

Process multiple payments in a single transaction for gas efficiency.

**Parameters:**
- `payments` (List[Payment]): List of Payment objects to process

**Returns:**
- `List[str]`: List of transaction hashes for each payment

**Raises:**
- `InsufficientFundsError`: If total amount exceeds balance
- `PaymentError`: If batch processing fails

**Example:**
```python
from x402_agent.types import Payment

payments = [
    Payment(amount=1.0, recipient="0xapi1...", memo="Weather API"),
    Payment(amount=2.0, recipient="0xapi2...", memo="Stock API"),
    Payment(amount=0.5, recipient="0xapi3...", memo="News API")
]

tx_hashes = wallet.batch_payments(payments)
print(f"Batch processed: {len(tx_hashes)} transactions")
```

### `estimate_gas_cost(amount, recipient)`

Estimate the gas cost for a payment transaction.

**Parameters:**
- `amount` (float): Payment amount in USDC
- `recipient` (str): Recipient address

**Returns:**
- `float`: Estimated gas cost in native tokens (ETH, SOL, etc.)

**Example:**
```python
gas_cost = wallet.estimate_gas_cost(5.0, "0xrecipient...")
print(f"Estimated gas: {gas_cost:.6f} ETH")
```

### `get_transaction_history(limit=100)`

Retrieve recent transaction history for the wallet.

**Parameters:**
- `limit` (int, optional): Maximum number of transactions to return. Defaults to 100

**Returns:**
- `List[dict]`: List of transaction records

**Example:**
```python
history = wallet.get_transaction_history(limit=50)
for tx in history:
    print(f"{tx['timestamp']}: {tx['type']} ${tx['amount']}")
```

### `transfer_to_wallet(amount, recipient_wallet)`

Transfer funds to another WalletManager instance.

**Parameters:**
- `amount` (float): Amount to transfer in USDC
- `recipient_wallet` (WalletManager): Recipient wallet manager

**Returns:**
- `str`: Transaction hash of the transfer

**Example:**
```python
other_wallet = WalletManager("0xother_key...", "base")
tx_hash = wallet.transfer_to_wallet(10.0, other_wallet)
```

### `sign_message(message)`

Sign a message with the wallet's private key for authentication.

**Parameters:**
- `message` (str): Message to sign

**Returns:**
- `str`: Signed message signature

**Example:**
```python
signature = wallet.sign_message("Authenticate agent access")
print(f"Signature: {signature}")
```

## Network-Specific Methods

### Base Network Methods

#### `get_base_transaction_receipt(tx_hash)`

Get transaction receipt from Base Network.

**Parameters:**
- `tx_hash` (str): Transaction hash

**Returns:**
- `dict`: Transaction receipt details

### Solana Network Methods

#### `get_solana_transaction_status(tx_hash)`

Get transaction status from Solana Network.

**Parameters:**
- `tx_hash` (str): Transaction signature

**Returns:**
- `dict`: Transaction status and details

## Security Features

### Private Key Management

- Private keys are stored in memory only
- No persistent storage of sensitive data
- Automatic memory cleanup on object destruction

### Transaction Security

- All transactions are signed locally
- Network requests use HTTPS/WSS only
- Transaction validation before submission

### Error Recovery

- Automatic retry for network failures
- Transaction status monitoring
- Graceful handling of insufficient funds

## Configuration

### Network Configuration

```python
# Custom RPC endpoints
wallet = WalletManager(
    private_key="0x...",
    network="base",
    rpc_url="https://custom-base-rpc.com"
)
```

### Gas Price Configuration

```python
# Set custom gas price for faster transactions
wallet.set_gas_price(gwei=20)  # Base Network
wallet.set_priority_fee(lamports=5000)  # Solana Network
```

## Error Handling

### Common Exceptions

#### `InsufficientFundsError`
Raised when wallet balance is too low for a transaction.

```python
try:
    wallet.make_payment(1000.0, "0xrecipient...")
except InsufficientFundsError as e:
    print(f"Not enough funds: {e}")
```

#### `NetworkError`
Raised when blockchain network is unreachable.

```python
try:
    balance = wallet.get_balance()
except NetworkError as e:
    print(f"Network issue: {e}")
```

#### `PaymentError`
Raised when payment processing fails.

```python
try:
    tx_hash = wallet.make_payment(5.0, "invalid_address")
except PaymentError as e:
    print(f"Payment failed: {e}")
```

## Performance Optimization

### Connection Pooling

```python
# Reuse connections for better performance
wallet.enable_connection_pooling()
```

### Batch Processing

```python
# Process multiple payments efficiently
payments = [...]  # List of payments
tx_hashes = wallet.batch_payments(payments)
```

### Caching

```python
# Enable balance caching for frequent checks
wallet.enable_balance_caching(ttl=30)  # 30 second cache
```

## Monitoring and Logging

### Transaction Monitoring

```python
def tx_callback(tx_hash, status):
    print(f"Transaction {tx_hash}: {status}")

wallet.add_transaction_callback(tx_callback)
```

### Balance Alerts

```python
def balance_alert(balance):
    if balance < 1.0:
        print(f"Low balance warning: ${balance}")

wallet.add_balance_callback(balance_alert)
```

## Thread Safety

The WalletManager class is thread-safe for all operations. Multiple threads can safely:

- Check balances concurrently
- Process payments simultaneously
- Access transaction history

## Best Practices

1. **Security**: Never log or store private keys
2. **Performance**: Use batch payments for multiple transactions
3. **Monitoring**: Set up balance alerts for low funds
4. **Error Handling**: Always handle network and payment errors
5. **Gas Management**: Monitor gas prices for cost optimization

## Examples

### Basic Usage

```python
from x402_agent.wallet import WalletManager

# Initialize wallet
wallet = WalletManager("0xprivate_key...", "base")

# Check balance
balance = wallet.get_balance()
print(f"Balance: ${balance}")

# Make payment
tx_hash = wallet.make_payment(1.0, "0xapi_provider...")
print(f"Payment sent: {tx_hash}")
```

### Advanced Usage

```python
from x402_agent.wallet import WalletManager
from x402_agent.types import Payment

# Initialize with custom configuration
wallet = WalletManager(
    private_key="0x...",
    network="base",
    rpc_url="https://custom-rpc.com"
)

# Set up monitoring
def monitor_transactions(tx_hash, status):
    print(f"TX {tx_hash}: {status}")

wallet.add_transaction_callback(monitor_transactions)

# Batch multiple payments
payments = [
    Payment(1.0, "0xapi1...", "Weather API"),
    Payment(2.0, "0xapi2...", "Stock API")
]

tx_hashes = wallet.batch_payments(payments)
print(f"Processed {len(tx_hashes)} payments")
```