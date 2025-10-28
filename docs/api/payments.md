# PaymentProcessor API Reference

The `PaymentProcessor` class handles HTTP 402 Payment Required responses and manages the payment flow for API access in the x402-Agent Framework.

## Class Definition

```python
class PaymentProcessor:
    """
    Processes HTTP 402 Payment Required responses and handles micropayments.
    
    Automatically detects payment requirements, processes payments through
    the wallet manager, and retries API calls after successful payment.
    """
```

## Constructor

### `__init__(wallet_manager, deferred_threshold=10)`

Initialize a new PaymentProcessor instance.

**Parameters:**
- `wallet_manager` (WalletManager): Wallet manager for payment operations
- `deferred_threshold` (int, optional): Number of payments to batch before processing. Defaults to 10

**Example:**
```python
from x402_agent.payments import PaymentProcessor
from x402_agent.wallet import WalletManager

wallet = WalletManager("0xprivate_key...", "base")
processor = PaymentProcessor(wallet, deferred_threshold=5)
```

## Properties

### `wallet_manager`
The wallet manager instance used for payments.

**Type:** `WalletManager`

### `deferred_threshold`
Number of payments to accumulate before batch processing.

**Type:** `int`

### `pending_payments`
List of payments waiting to be processed.

**Type:** `List[PendingPayment]`

### `payment_history`
History of completed payments.

**Type:** `List[PaymentRecord]`

## Methods

### `process_request(url, method="GET", headers=None, data=None, **kwargs)`

Process an HTTP request with automatic payment handling for 402 responses.

**Parameters:**
- `url` (str): Target API endpoint URL
- `method` (str, optional): HTTP method. Defaults to "GET"
- `headers` (dict, optional): Additional HTTP headers
- `data` (Any, optional): Request body data
- `**kwargs`: Additional arguments passed to requests

**Returns:**
- `requests.Response`: HTTP response after payment (if required)

**Raises:**
- `PaymentError`: If payment processing fails
- `InsufficientFundsError`: If wallet balance is too low
- `InvalidPaymentRequestError`: If 402 response format is invalid

**Example:**
```python
response = processor.process_request(
    url="https://api.weather.com/v1/current",
    method="GET",
    headers={"User-Agent": "x402-agent/1.0"}
)

if response.status_code == 200:
    data = response.json()
    print(f"Weather data: {data}")
```

### `handle_402_response(response)`

Parse and handle an HTTP 402 Payment Required response.

**Parameters:**
- `response` (requests.Response): HTTP 402 response to process

**Returns:**
- `PaymentRequest`: Parsed payment request details

**Raises:**
- `InvalidPaymentRequestError`: If 402 headers are missing or invalid

**Example:**
```python
import requests

response = requests.get("https://api.example.com/data")
if response.status_code == 402:
    payment_request = processor.handle_402_response(response)
    print(f"Payment required: ${payment_request.amount}")
```

### `make_payment(payment_request)`

Execute a payment for an API access request.

**Parameters:**
- `payment_request` (PaymentRequest): Payment details from 402 response

**Returns:**
- `PaymentResult`: Result of the payment transaction

**Raises:**
- `PaymentError`: If payment processing fails
- `InsufficientFundsError`: If wallet balance is insufficient

**Example:**
```python
payment_result = processor.make_payment(payment_request)
print(f"Payment completed: {payment_result.transaction_hash}")
```

### `add_deferred_payment(payment_request)`

Add a payment to the deferred batch processing queue.

**Parameters:**
- `payment_request` (PaymentRequest): Payment to defer

**Returns:**
- `str`: Unique identifier for the deferred payment

**Example:**
```python
payment_id = processor.add_deferred_payment(payment_request)
print(f"Payment deferred: {payment_id}")
```

### `process_deferred_payments()`

Process all pending deferred payments in a batch transaction.

**Returns:**
- `List[PaymentResult]`: Results of all processed payments

**Raises:**
- `PaymentError`: If batch processing fails

**Example:**
```python
results = processor.process_deferred_payments()
print(f"Processed {len(results)} deferred payments")
```

### `get_payment_summary()`

Get a summary of payment activity and statistics.

**Returns:**
- `dict`: Payment summary with statistics

**Example:**
```python
summary = processor.get_payment_summary()
print(f"Total payments: {summary['total_count']}")
print(f"Total amount: ${summary['total_amount']}")
print(f"Average payment: ${summary['average_amount']}")
```

### `export_payment_history(start_date=None, end_date=None)`

Export payment history for analysis and reporting.

**Parameters:**
- `start_date` (datetime, optional): Start date for export
- `end_date` (datetime, optional): End date for export

**Returns:**
- `List[dict]`: List of payment records

**Example:**
```python
from datetime import datetime, timedelta

# Export last 30 days
start = datetime.now() - timedelta(days=30)
history = processor.export_payment_history(start_date=start)

for payment in history:
    print(f"{payment['timestamp']}: ${payment['amount']} to {payment['recipient']}")
```

## Payment Request Format

### HTTP 402 Response Headers

The processor expects specific headers in 402 responses:

```http
HTTP/1.1 402 Payment Required
X-Payment-Amount: 0.01
X-Payment-Address: 0x1234567890abcdef...
X-Payment-Currency: USDC
X-Payment-Network: base
X-Payment-Memo: Weather API access
Content-Type: application/json

{
  "error": "Payment required",
  "message": "This API requires payment for access",
  "payment": {
    "amount": 0.01,
    "currency": "USDC",
    "address": "0x1234567890abcdef...",
    "network": "base",
    "memo": "Weather API access"
  }
}
```

### PaymentRequest Object

```python
@dataclass
class PaymentRequest:
    amount: float
    recipient: str
    currency: str = "USDC"
    network: str = "base"
    memo: str = ""
    api_endpoint: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
```

### PaymentResult Object

```python
@dataclass
class PaymentResult:
    transaction_hash: str
    amount: float
    recipient: str
    network: str
    timestamp: datetime
    gas_cost: float
    status: str  # "success", "pending", "failed"
```

## Deferred Payment System

### How It Works

1. **Accumulation**: Payments are collected until threshold is reached
2. **Batching**: Multiple payments are combined into a single transaction
3. **Processing**: Batch transaction is submitted to blockchain
4. **Confirmation**: All payments are confirmed together

### Benefits

- **Gas Efficiency**: Reduced transaction costs through batching
- **Performance**: Fewer blockchain interactions
- **Reliability**: Atomic batch processing

### Configuration

```python
# Configure deferred payments
processor = PaymentProcessor(
    wallet_manager=wallet,
    deferred_threshold=20,  # Batch every 20 payments
)

# Enable automatic processing
processor.enable_auto_processing(interval=300)  # Every 5 minutes
```

## Callbacks and Events

### Payment Callbacks

```python
def payment_callback(payment_result):
    print(f"Payment completed: {payment_result.transaction_hash}")

processor.add_payment_callback(payment_callback)
```

### Error Callbacks

```python
def error_callback(error, context):
    print(f"Payment error: {error} in {context}")
    # Send alert to monitoring system

processor.add_error_callback(error_callback)
```

### Batch Processing Callbacks

```python
def batch_callback(batch_results):
    total_amount = sum(r.amount for r in batch_results)
    print(f"Batch processed: ${total_amount} in {len(batch_results)} payments")

processor.add_batch_callback(batch_callback)
```

## Error Handling

### Payment Errors

#### `InvalidPaymentRequestError`
Raised when 402 response format is invalid.

```python
try:
    payment_request = processor.handle_402_response(response)
except InvalidPaymentRequestError as e:
    print(f"Invalid payment request: {e}")
```

#### `PaymentTimeoutError`
Raised when payment processing times out.

```python
try:
    result = processor.make_payment(payment_request)
except PaymentTimeoutError as e:
    print(f"Payment timed out: {e}")
```

#### `DuplicatePaymentError`
Raised when attempting to process the same payment twice.

```python
try:
    processor.make_payment(payment_request)
except DuplicatePaymentError as e:
    print(f"Payment already processed: {e}")
```

## Security Features

### Payment Validation

- Amount validation (positive, reasonable limits)
- Recipient address validation
- Network compatibility checks
- Duplicate payment prevention

### Request Security

- HTTPS enforcement for all API calls
- Request signing for authentication
- Rate limiting protection
- Timeout handling

### Transaction Security

- Transaction hash verification
- Confirmation monitoring
- Automatic retry on failure
- Gas price optimization

## Performance Optimization

### Connection Pooling

```python
# Enable connection pooling for better performance
processor.enable_connection_pooling(pool_size=10)
```

### Caching

```python
# Cache payment requests to avoid duplicates
processor.enable_request_caching(ttl=300)  # 5 minute cache
```

### Async Processing

```python
# Enable asynchronous payment processing
processor.enable_async_processing()
```

## Monitoring and Analytics

### Real-time Monitoring

```python
# Monitor payment processing in real-time
def monitor_payments(payment_result):
    if payment_result.amount > 1.0:
        print(f"High-value payment: ${payment_result.amount}")

processor.add_payment_callback(monitor_payments)
```

### Analytics Dashboard

```python
# Get detailed analytics
analytics = processor.get_analytics()
print(f"Success rate: {analytics['success_rate']:.2%}")
print(f"Average processing time: {analytics['avg_processing_time']:.2f}s")
print(f"Total gas spent: {analytics['total_gas_cost']:.6f} ETH")
```

## Configuration Options

### Environment Variables

```bash
# Payment processing configuration
export X402_DEFERRED_THRESHOLD=10
export X402_PAYMENT_TIMEOUT=30
export X402_MAX_RETRY_ATTEMPTS=3
export X402_ENABLE_BATCH_PROCESSING=true
```

### Configuration File

```yaml
# ~/.x402/config.yaml
payment_processor:
  deferred_threshold: 10
  payment_timeout: 30
  max_retry_attempts: 3
  enable_batch_processing: true
  auto_process_interval: 300
```

## Best Practices

1. **Batch Processing**: Use deferred payments for high-frequency API usage
2. **Error Handling**: Always handle payment errors gracefully
3. **Monitoring**: Set up callbacks for payment tracking
4. **Security**: Validate all payment requests before processing
5. **Performance**: Use connection pooling for better throughput

## Examples

### Basic Payment Processing

```python
from x402_agent.payments import PaymentProcessor
from x402_agent.wallet import WalletManager
import requests

# Initialize components
wallet = WalletManager("0xprivate_key...", "base")
processor = PaymentProcessor(wallet)

# Make API call with automatic payment
response = processor.process_request("https://api.weather.com/v1/current")

if response.status_code == 200:
    weather_data = response.json()
    print(f"Temperature: {weather_data['temperature']}°F")
```

### Deferred Payment Processing

```python
# Configure for batch processing
processor = PaymentProcessor(wallet, deferred_threshold=5)

# Make multiple API calls
for i in range(10):
    response = processor.process_request(f"https://api.data.com/v1/item/{i}")
    # Payments are batched automatically

# Process remaining deferred payments
processor.process_deferred_payments()
```

### Advanced Monitoring

```python
# Set up comprehensive monitoring
def payment_monitor(result):
    print(f"Payment: ${result.amount} -> {result.recipient}")
    
def error_monitor(error, context):
    print(f"Error in {context}: {error}")
    
def batch_monitor(results):
    total = sum(r.amount for r in results)
    print(f"Batch: {len(results)} payments, ${total} total")

processor.add_payment_callback(payment_monitor)
processor.add_error_callback(error_monitor)
processor.add_batch_callback(batch_monitor)

# Enable analytics
analytics = processor.get_analytics()
print(f"Payment success rate: {analytics['success_rate']:.2%}")
```