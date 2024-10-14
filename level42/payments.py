"""
Payment processing system for HTTP 402 handling.

This module handles L42 micropayment flows, deferred payment batching,
and transaction logging.
"""

from typing import List, Dict, Optional, Tuple, Any
import requests
import time
import logging
import sqlite3
import os
from datetime import datetime, timedelta
from .wallet import WalletManager, Payment
from .monitoring import Level42Logger, DebugConfig


from .exceptions import (
    PaymentError,
    InsufficientFundsError,
    NetworkError,
    TransactionError,
    PaymentValidationError,
    HTTP402Error
)


class PaymentProcessor:
    """
    Processes HTTP 402 responses and manages micropayment flows.
    
    Handles automatic payment processing when encountering HTTP 402 status codes
    and provides deferred payment batching for efficiency.
    """
    
    def __init__(self, wallet_manager: WalletManager, db_path: str = "level42_payments.db", 
                 debug_config: DebugConfig = None):
        """
        Initialize with wallet manager and database.
        
        Args:
            wallet_manager: WalletManager instance for processing payments
            db_path: Path to SQLite database for transaction logging
            debug_config: Debug configuration for logging
        """
        self.wallet_manager = wallet_manager
        self.deferred_payments: List[Dict] = []
        self.payment_threshold = 10
        self.db_path = db_path
        self.logger = Level42Logger(debug_config or DebugConfig())
        self._init_database()
    
    def handle_402_response(self, response: requests.Response) -> requests.Response:
        """
        Process HTTP 402 and retry with payment.
        
        Args:
            response: HTTP 402 response object
            
        Returns:
            Retry response after payment
            
        Raises:
            PaymentValidationError: If payment requirements cannot be parsed
            InsufficientFundsError: If wallet has insufficient funds
            NetworkError: If network operations fail
            TransactionError: If payment transaction fails
        """
        if response.status_code != 402:
            return response
        
        # Parse payment requirements from headers
        try:
            payment_info = self._parse_payment_headers(response)
        except ValueError as e:
            raise PaymentValidationError(f"Invalid 402 response headers: {str(e)}")
        
        # Check balance before attempting payment
        try:
            current_balance = self.wallet_manager.get_balance()
            if current_balance < payment_info['amount']:
                raise InsufficientFundsError(
                    required=payment_info['amount'],
                    available=current_balance
                )
        except InsufficientFundsError:
            raise
        except Exception as e:
            raise NetworkError(f"Failed to check wallet balance: {str(e)}")
        
        # Execute payment with error handling
        payment = Payment(
            amount=payment_info['amount'],
            recipient=payment_info['recipient'],
            tool_name=payment_info.get('tool_name', 'unknown'),
            timestamp=datetime.now(),
            status='pending',
            tx_hash=''
        )
        
        try:
            tx_hash = self.wallet_manager.make_payment(
                payment_info['amount'], 
                payment_info['recipient']
            )
            
            # Update payment status
            payment.status = 'completed'
            payment.tx_hash = tx_hash
            self._log_payments([payment])
            
            # Log successful payment
            self.logger.log_payment(
                amount=payment.amount,
                recipient=payment.recipient,
                tool_name=payment.tool_name,
                status='completed',
                tx_hash=tx_hash
            )
            
            # Retry original request with payment proof
            return self._retry_request_with_payment(response.request, tx_hash)
            
        except ValueError as e:
            payment.status = 'failed'
            self._log_payments([payment])
            
            # Log failed payment
            self.logger.log_payment(
                amount=payment.amount,
                recipient=payment.recipient,
                tool_name=payment.tool_name,
                status='failed',
                error=str(e)
            )
            
            if "insufficient" in str(e).lower():
                raise InsufficientFundsError(
                    required=payment_info['amount'],
                    available=current_balance,
                    message=str(e)
                )
            else:
                raise PaymentValidationError(f"Payment validation failed: {str(e)}")
        
        except Exception as e:
            payment.status = 'failed'
            self._log_payments([payment])
            
            # Log failed payment
            self.logger.log_payment(
                amount=payment.amount,
                recipient=payment.recipient,
                tool_name=payment.tool_name,
                status='failed',
                error=str(e)
            )
            
            # Log error with context
            self.logger.log_error(e, {
                'payment_amount': payment.amount,
                'recipient': payment.recipient,
                'tool_name': payment.tool_name
            })
            
            # Categorize the error
            error_msg = str(e).lower()
            if "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                raise NetworkError(f"Payment network error: {str(e)}")
            elif "transaction" in error_msg or "gas" in error_msg or "nonce" in error_msg:
                raise TransactionError(f"Payment transaction failed: {str(e)}")
            else:
                raise PaymentError(f"Payment failed: {str(e)}")
    
    def _parse_payment_headers(self, response: requests.Response) -> Dict:
        """
        Parse payment requirements from HTTP 402 response headers.
        
        Args:
            response: HTTP 402 response
            
        Returns:
            Dictionary with payment requirements
            
        Raises:
            ValueError: If required headers are missing or invalid
        """
        headers = response.headers
        
        # Standard L42 headers
        amount_header = headers.get('X-Payment-Amount') or headers.get('Payment-Amount')
        recipient_header = headers.get('X-Payment-Address') or headers.get('Payment-Address')
        
        if not amount_header:
            raise ValueError("Missing payment amount in 402 response headers")
        
        if not recipient_header:
            raise ValueError("Missing payment address in 402 response headers")
        
        try:
            amount = float(amount_header)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid payment amount: {amount_header}")
        
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        # Validate recipient address format (basic check)
        recipient = recipient_header.strip()
        if not recipient.startswith('0x') or len(recipient) != 42:
            raise ValueError(f"Invalid payment address format: {recipient}")
        
        # Optional headers
        tool_name = headers.get('X-Tool-Name', headers.get('Tool-Name', 'unknown'))
        
        return {
            'amount': amount,
            'recipient': recipient,
            'tool_name': tool_name
        }
    
    def _retry_request_with_payment(self, original_request, tx_hash: str) -> requests.Response:
        """
        Retry original request with payment proof using exponential backoff.
        
        Args:
            original_request: Original request object
            tx_hash: Transaction hash as payment proof
            
        Returns:
            Response from retry attempt
            
        Raises:
            NetworkError: If retry fails due to network issues
            PaymentError: If payment was not accepted
        """
        # Prepare retry request with payment proof
        retry_headers = dict(original_request.headers) if original_request.headers else {}
        retry_headers['X-Payment-Hash'] = tx_hash
        retry_headers['Payment-Hash'] = tx_hash  # Alternative header name
        
        # Add small delay to allow transaction confirmation
        time.sleep(2)
        
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Calculate exponential backoff delay
                if attempt > 0:
                    delay = base_delay * (2 ** (attempt - 1))
                    logging.info(f"Retrying request after {delay}s delay (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                
                # Recreate the request with payment proof
                retry_response = requests.request(
                    method=original_request.method,
                    url=original_request.url,
                    headers=retry_headers,
                    data=original_request.body,
                    timeout=30
                )
                
                # If successful or different error, return response
                if retry_response.status_code != 402:
                    logging.info(f"Request retry successful after payment (status: {retry_response.status_code})")
                    return retry_response
                
                # If still 402, log and continue to next retry
                logging.warning(f"Request still returned 402 after payment (attempt {attempt + 1}/{max_retries})")
                
            except requests.Timeout as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"Request timeout after payment", attempt + 1, max_retries)
                logging.warning(f"Request timeout on attempt {attempt + 1}, retrying...")
                
            except requests.ConnectionError as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"Connection error after payment: {str(e)}", attempt + 1, max_retries)
                logging.warning(f"Connection error on attempt {attempt + 1}, retrying...")
                
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise NetworkError(f"Request failed after payment: {str(e)}", attempt + 1, max_retries)
                logging.warning(f"Request error on attempt {attempt + 1}, retrying...")
        
        raise PaymentError("Payment was not accepted - request still returned 402 after payment and retries")
    
    def add_deferred_payment(self, amount: float, recipient: str, tool_name: str = "") -> None:
        """
        Add payment to deferred batch queue.
        
        Args:
            amount: Payment amount in USDC
            recipient: Payment recipient address
            tool_name: Name of tool requiring payment
            
        Raises:
            ValueError: If amount is invalid or recipient address is malformed
        """
        # Validate inputs
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if not recipient or not recipient.startswith('0x') or len(recipient) != 42:
            raise ValueError(f"Invalid recipient address format: {recipient}")
        
        payment_data = {
            "amount": amount,
            "recipient": recipient,
            "tool_name": tool_name,
            "timestamp": datetime.now()
        }
        self.deferred_payments.append(payment_data)
        
        logging.info(f"Added deferred payment: {amount} USDC to {recipient} for {tool_name}")
        
        # Auto-process if threshold reached (10 payments)
        if len(self.deferred_payments) >= self.payment_threshold:
            logging.info(f"Threshold reached ({self.payment_threshold}), processing deferred payments")
            self.process_deferred_payments()
    
    def process_deferred_payments(self) -> bool:
        """
        Process all deferred payments in batch with rollback on failure.
        
        Returns:
            True if all payments successful, False otherwise
            
        Raises:
            InsufficientFundsError: If wallet has insufficient funds for batch
            NetworkError: If network operations fail
            PaymentError: If batch processing fails completely
        """
        if not self.deferred_payments:
            logging.info("No deferred payments to process")
            return True
        
        payment_count = len(self.deferred_payments)
        total_amount = sum(p["amount"] for p in self.deferred_payments)
        
        logging.info(f"Processing {payment_count} deferred payments totaling {total_amount} USDC")
        
        # Check balance before processing batch
        try:
            current_balance = self.wallet_manager.get_balance()
            if current_balance < total_amount:
                raise InsufficientFundsError(
                    required=total_amount,
                    available=current_balance,
                    message=f"Insufficient funds for batch payment: need {total_amount} USDC, have {current_balance} USDC"
                )
        except InsufficientFundsError:
            raise
        except Exception as e:
            raise NetworkError(f"Failed to check balance before batch processing: {str(e)}")
        
        # Convert to Payment objects
        payments = [
            Payment(
                amount=p["amount"],
                recipient=p["recipient"],
                tool_name=p["tool_name"],
                timestamp=p["timestamp"],
                status="pending"
            )
            for p in self.deferred_payments
        ]
        
        # Store original deferred payments for potential rollback
        original_deferred = self.deferred_payments.copy()
        
        try:
            # Process batch payment
            tx_hashes = self.wallet_manager.batch_payments(payments)
            
            # Update payment status based on transaction results
            successful_payments = 0
            failed_payments = []
            
            for payment, tx_hash in zip(payments, tx_hashes):
                payment.tx_hash = tx_hash
                if tx_hash and not tx_hash.startswith("FAILED"):
                    payment.status = "completed"
                    successful_payments += 1
                else:
                    payment.status = "failed"
                    failed_payments.append(payment)
            
            # Clear deferred payments after processing
            self.deferred_payments.clear()
            
            # Log all payments
            self._log_payments(payments)
            
            success_rate = successful_payments / len(payments)
            logging.info(f"Batch processing complete: {successful_payments}/{len(payments)} successful ({success_rate:.1%})")
            
            # If some payments failed, attempt individual retries
            if failed_payments and successful_payments > 0:
                logging.info(f"Attempting individual retries for {len(failed_payments)} failed payments")
                self._retry_failed_payments(failed_payments)
            
            return success_rate == 1.0
            
        except ValueError as e:
            # Rollback: restore deferred payments
            self.deferred_payments = original_deferred
            
            # Mark all payments as failed
            for payment in payments:
                payment.status = "failed"
            self._log_payments(payments)
            
            if "insufficient" in str(e).lower():
                raise InsufficientFundsError(
                    required=total_amount,
                    available=current_balance,
                    message=f"Batch payment failed due to insufficient funds: {str(e)}"
                )
            else:
                raise PaymentError(f"Batch payment validation failed: {str(e)}")
        
        except Exception as e:
            # Rollback: restore deferred payments
            self.deferred_payments = original_deferred
            
            logging.error(f"Batch payment processing failed: {str(e)}")
            
            # Mark all payments as failed
            for payment in payments:
                payment.status = "failed"
            self._log_payments(payments)
            
            # Categorize the error
            error_msg = str(e).lower()
            if "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                raise NetworkError(f"Batch payment network error: {str(e)}")
            else:
                raise PaymentError(f"Batch payment processing failed: {str(e)}")
    
    def _retry_failed_payments(self, failed_payments: List[Payment]) -> None:
        """
        Retry individual payments that failed in batch processing.
        
        Args:
            failed_payments: List of payments that failed in batch
        """
        for payment in failed_payments:
            try:
                logging.info(f"Retrying individual payment: {payment.amount} USDC to {payment.recipient}")
                
                tx_hash = self.wallet_manager.make_payment(
                    payment.amount,
                    payment.recipient
                )
                
                # Update payment status
                payment.status = "completed"
                payment.tx_hash = tx_hash
                payment.timestamp = datetime.now()  # Update timestamp for retry
                
                logging.info(f"Individual payment retry successful: {tx_hash}")
                
            except Exception as e:
                logging.error(f"Individual payment retry failed for {payment.recipient}: {str(e)}")
                payment.status = "failed"
                payment.timestamp = datetime.now()
        
        # Log all retry attempts
        self._log_payments(failed_payments)
    
    def force_process_deferred_payments(self) -> bool:
        """
        Manually trigger processing of deferred payments regardless of threshold.
        
        Returns:
            True if all payments successful, False otherwise
        """
        logging.info("Manually triggering deferred payment processing")
        return self.process_deferred_payments()
    
    def _init_database(self) -> None:
        """Initialize SQLite database for transaction tracking."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create transactions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payment_transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent_id TEXT,
                        tool_name TEXT,
                        amount REAL NOT NULL,
                        recipient TEXT NOT NULL,
                        tx_hash TEXT,
                        status TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index for faster queries
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON payment_transactions(timestamp)
                ''')
                
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_agent_tool 
                    ON payment_transactions(agent_id, tool_name)
                ''')
                
                conn.commit()
                logging.info(f"Payment database initialized at {self.db_path}")
                
        except sqlite3.Error as e:
            logging.error(f"Failed to initialize payment database: {str(e)}")
            raise RuntimeError(f"Database initialization failed: {str(e)}")
    
    def _log_payments(self, payments: List[Payment]) -> None:
        """
        Log payment transactions for audit purposes.
        
        Args:
            payments: List of payments to log
        """
        if not payments:
            return
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare data for batch insert
                payment_data = [
                    (
                        self.wallet_manager.get_address(),  # Use wallet address as agent_id
                        payment.tool_name,
                        payment.amount,
                        payment.recipient,
                        payment.tx_hash,
                        payment.status,
                        payment.timestamp.isoformat()
                    )
                    for payment in payments
                ]
                
                # Batch insert payments
                cursor.executemany('''
                    INSERT INTO payment_transactions 
                    (agent_id, tool_name, amount, recipient, tx_hash, status, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', payment_data)
                
                conn.commit()
                logging.info(f"Logged {len(payments)} payment transactions to database")
                
        except sqlite3.Error as e:
            logging.error(f"Failed to log payments to database: {str(e)}")
            # Don't raise exception here to avoid breaking payment flow
    
    def get_payment_history(self, agent_id: Optional[str] = None, 
                          tool_name: Optional[str] = None,
                          days: int = 30) -> List[Dict]:
        """
        Get payment history with optional filtering.
        
        Args:
            agent_id: Filter by agent ID (wallet address)
            tool_name: Filter by tool name
            days: Number of days to look back
            
        Returns:
            List of payment records
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with optional filters
                query = '''
                    SELECT agent_id, tool_name, amount, recipient, tx_hash, 
                           status, timestamp, created_at
                    FROM payment_transactions 
                    WHERE timestamp >= ?
                '''
                params = [datetime.now() - timedelta(days=days)]
                
                if agent_id:
                    query += ' AND agent_id = ?'
                    params.append(agent_id)
                
                if tool_name:
                    query += ' AND tool_name = ?'
                    params.append(tool_name)
                
                query += ' ORDER BY timestamp DESC'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to dictionaries
                columns = ['agent_id', 'tool_name', 'amount', 'recipient', 
                          'tx_hash', 'status', 'timestamp', 'created_at']
                
                return [dict(zip(columns, row)) for row in rows]
                
        except sqlite3.Error as e:
            logging.error(f"Failed to retrieve payment history: {str(e)}")
            return []
    
    def get_spending_analytics(self, agent_id: Optional[str] = None, 
                             days: int = 30) -> Dict:
        """
        Get spending analytics and usage tracking.
        
        Args:
            agent_id: Filter by agent ID (wallet address)
            days: Number of days to analyze
            
        Returns:
            Dictionary with spending analytics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Base query conditions
                base_query = '''
                    FROM payment_transactions 
                    WHERE timestamp >= ? AND status = 'completed'
                '''
                params = [datetime.now() - timedelta(days=days)]
                
                if agent_id:
                    base_query += ' AND agent_id = ?'
                    params.append(agent_id)
                
                # Total spending
                cursor.execute(f'SELECT SUM(amount) {base_query}', params)
                total_spent = cursor.fetchone()[0] or 0.0
                
                # Transaction count
                cursor.execute(f'SELECT COUNT(*) {base_query}', params)
                transaction_count = cursor.fetchone()[0] or 0
                
                # Average transaction amount
                avg_amount = total_spent / transaction_count if transaction_count > 0 else 0.0
                
                # Spending by tool
                cursor.execute(f'''
                    SELECT tool_name, SUM(amount) as total, COUNT(*) as count
                    {base_query}
                    GROUP BY tool_name
                    ORDER BY total DESC
                ''', params)
                
                tool_spending = [
                    {'tool_name': row[0], 'total_spent': row[1], 'transaction_count': row[2]}
                    for row in cursor.fetchall()
                ]
                
                # Daily spending trend
                cursor.execute(f'''
                    SELECT DATE(timestamp) as date, SUM(amount) as daily_total
                    {base_query}
                    GROUP BY DATE(timestamp)
                    ORDER BY date DESC
                    LIMIT 7
                ''', params)
                
                daily_spending = [
                    {'date': row[0], 'amount': row[1]}
                    for row in cursor.fetchall()
                ]
                
                return {
                    'period_days': days,
                    'total_spent': total_spent,
                    'transaction_count': transaction_count,
                    'average_transaction': avg_amount,
                    'spending_by_tool': tool_spending,
                    'daily_spending': daily_spending
                }
                
        except sqlite3.Error as e:
            logging.error(f"Failed to generate spending analytics: {str(e)}")
            return {
                'period_days': days,
                'total_spent': 0.0,
                'transaction_count': 0,
                'average_transaction': 0.0,
                'spending_by_tool': [],
                'daily_spending': []
            }
    
    def get_pending_payment_count(self) -> int:
        """Get number of pending deferred payments."""
        return len(self.deferred_payments)
    
    def get_pending_payment_total(self) -> float:
        """Get total amount of pending deferred payments."""
        return sum(p["amount"] for p in self.deferred_payments)
    
    def enable_debug_mode(self, debug_config: DebugConfig = None):
        """
        Enable debug mode with optional configuration.
        
        Args:
            debug_config: Debug configuration (uses default if None)
        """
        if debug_config is None:
            debug_config = DebugConfig(enabled=True, log_level="DEBUG")
        
        self.logger = Level42Logger(debug_config)
        self.logger.log_debug("Debug mode enabled for PaymentProcessor")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information about current state.
        
        Returns:
            Dictionary with debug information
        """
        return {
            'pending_payments_count': len(self.deferred_payments),
            'pending_payments_total': self.get_pending_payment_total(),
            'payment_threshold': self.payment_threshold,
            'database_path': self.db_path,
            'wallet_address': self.wallet_manager.get_address(),
            'wallet_network': self.wallet_manager.network
        }# Payment processing fixes
# Payment batching optimizations
