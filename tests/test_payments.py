"""
Unit tests for payment processing system.

Tests HTTP 402 response parsing, payment flow, deferred payment batching,
and payment logging functionality.
"""

import pytest
import sqlite3
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests

from x402_agent.payments import PaymentProcessor
from x402_agent.wallet import WalletManager, Payment


class TestPaymentProcessor:
    """Test cases for PaymentProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Mock wallet manager
        self.mock_wallet = Mock(spec=WalletManager)
        self.mock_wallet.get_address.return_value = "0x742d35Cc6634C0532925a3b8D4C9db96C4b5Da5e"
        
        # Create processor with test database
        self.processor = PaymentProcessor(self.mock_wallet, self.temp_db.name)
        
        # Test data
        self.test_recipient = "0x8ba1f109551bD432803012645Hac136c5C1b5A5e"
        self.test_tx_hash = "0xabc123def456"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_processor_initialization(self):
        """Test PaymentProcessor initialization."""
        assert self.processor.wallet_manager == self.mock_wallet
        assert self.processor.payment_threshold == 10
        assert len(self.processor.deferred_payments) == 0
        
        # Verify database was created
        assert os.path.exists(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database schema creation."""
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            
            # Check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert 'payment_transactions' in tables
            
            # Check table structure
            cursor.execute("PRAGMA table_info(payment_transactions)")
            columns = [row[1] for row in cursor.fetchall()]
            
            expected_columns = ['id', 'agent_id', 'tool_name', 'amount', 
                              'recipient', 'tx_hash', 'status', 'timestamp', 'created_at']
            for col in expected_columns:
                assert col in columns


class TestHTTP402Handling:
    """Test cases for HTTP 402 response handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.mock_wallet = Mock(spec=WalletManager)
        self.mock_wallet.get_address.return_value = "0x742d35Cc6634C0532925a3b8D4C9db96C4b5Da5e"
        self.mock_wallet.make_payment.return_value = "0xabc123def456"
        
        self.processor = PaymentProcessor(self.mock_wallet, self.temp_db.name)
        
        self.test_recipient = "0x8ba1f109551bD432803012645Hac136c5C1b5A5e"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_parse_payment_headers_success(self):
        """Test successful parsing of payment headers."""
        mock_response = Mock()
        mock_response.headers = {
            'X-Payment-Amount': '0.50',
            'X-Payment-Address': self.test_recipient,
            'X-Tool-Name': 'test-api'
        }
        
        payment_info = self.processor._parse_payment_headers(mock_response)
        
        assert payment_info['amount'] == 0.50
        assert payment_info['recipient'] == self.test_recipient
        assert payment_info['tool_name'] == 'test-api'
    
    def test_parse_payment_headers_alternative_names(self):
        """Test parsing with alternative header names."""
        mock_response = Mock()
        mock_response.headers = {
            'Payment-Amount': '1.25',
            'Payment-Address': self.test_recipient,
            'Tool-Name': 'alt-api'
        }
        
        payment_info = self.processor._parse_payment_headers(mock_response)
        
        assert payment_info['amount'] == 1.25
        assert payment_info['recipient'] == self.test_recipient
        assert payment_info['tool_name'] == 'alt-api'
    
    def test_parse_payment_headers_missing_amount(self):
        """Test parsing with missing payment amount."""
        mock_response = Mock()
        mock_response.headers = {
            'X-Payment-Address': self.test_recipient
        }
        
        with pytest.raises(ValueError, match="Missing payment amount"):
            self.processor._parse_payment_headers(mock_response)
    
    def test_parse_payment_headers_missing_address(self):
        """Test parsing with missing payment address."""
        mock_response = Mock()
        mock_response.headers = {
            'X-Payment-Amount': '0.50'
        }
        
        with pytest.raises(ValueError, match="Missing payment address"):
            self.processor._parse_payment_headers(mock_response)
    
    def test_parse_payment_headers_invalid_amount(self):
        """Test parsing with invalid payment amount."""
        mock_response = Mock()
        mock_response.headers = {
            'X-Payment-Amount': 'invalid',
            'X-Payment-Address': self.test_recipient
        }
        
        with pytest.raises(ValueError, match="Invalid payment amount"):
            self.processor._parse_payment_headers(mock_response)
    
    def test_parse_payment_headers_negative_amount(self):
        """Test parsing with negative payment amount."""
        mock_response = Mock()
        mock_response.headers = {
            'X-Payment-Amount': '-0.50',
            'X-Payment-Address': self.test_recipient
        }
        
        with pytest.raises(ValueError, match="Payment amount must be positive"):
            self.processor._parse_payment_headers(mock_response)
    
    def test_parse_payment_headers_invalid_address(self):
        """Test parsing with invalid payment address."""
        mock_response = Mock()
        mock_response.headers = {
            'X-Payment-Amount': '0.50',
            'X-Payment-Address': 'invalid_address'
        }
        
        with pytest.raises(ValueError, match="Invalid payment address format"):
            self.processor._parse_payment_headers(mock_response)
    
    @patch('requests.request')
    @patch('time.sleep')
    def test_handle_402_response_success(self, mock_sleep, mock_request):
        """Test successful HTTP 402 handling."""
        # Mock original 402 response
        mock_402_response = Mock()
        mock_402_response.status_code = 402
        mock_402_response.headers = {
            'X-Payment-Amount': '0.50',
            'X-Payment-Address': self.test_recipient,
            'X-Tool-Name': 'test-api'
        }
        mock_402_response.request = Mock()
        mock_402_response.request.method = 'GET'
        mock_402_response.request.url = 'https://api.example.com/test'
        mock_402_response.request.headers = {}
        mock_402_response.request.body = None
        
        # Mock successful retry response
        mock_success_response = Mock()
        mock_success_response.status_code = 200
        mock_request.return_value = mock_success_response
        
        result = self.processor.handle_402_response(mock_402_response)
        
        # Verify payment was made
        self.mock_wallet.make_payment.assert_called_once_with(0.50, self.test_recipient)
        
        # Verify request was retried with payment proof
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert 'X-Payment-Hash' in call_args[1]['headers']
        assert call_args[1]['headers']['X-Payment-Hash'] == "0xabc123def456"
        
        assert result == mock_success_response
    
    def test_handle_402_response_non_402(self):
        """Test handling non-402 response."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        result = self.processor.handle_402_response(mock_response)
        
        assert result == mock_response
        self.mock_wallet.make_payment.assert_not_called()
    
    def test_handle_402_response_payment_failure(self):
        """Test HTTP 402 handling with payment failure."""
        mock_402_response = Mock()
        mock_402_response.status_code = 402
        mock_402_response.headers = {
            'X-Payment-Amount': '0.50',
            'X-Payment-Address': self.test_recipient
        }
        
        # Mock payment failure
        self.mock_wallet.make_payment.side_effect = RuntimeError("Insufficient funds")
        
        with pytest.raises(RuntimeError, match="Payment failed"):
            self.processor.handle_402_response(mock_402_response)
    
    @patch('requests.request')
    @patch('time.sleep')
    def test_retry_request_with_payment_multiple_attempts(self, mock_sleep, mock_request):
        """Test request retry with multiple attempts."""
        # Mock original request
        mock_original_request = Mock()
        mock_original_request.method = 'POST'
        mock_original_request.url = 'https://api.example.com/test'
        mock_original_request.headers = {'Content-Type': 'application/json'}
        mock_original_request.body = '{"test": "data"}'
        
        # Mock responses: first two return 402, third succeeds
        mock_responses = [Mock(), Mock(), Mock()]
        mock_responses[0].status_code = 402
        mock_responses[1].status_code = 402
        mock_responses[2].status_code = 200
        mock_request.side_effect = mock_responses
        
        result = self.processor._retry_request_with_payment(mock_original_request, "0xabc123")
        
        # Should have made 3 attempts
        assert mock_request.call_count == 3
        assert result == mock_responses[2]
    
    @patch('requests.request')
    @patch('time.sleep')
    def test_retry_request_max_retries_exceeded(self, mock_sleep, mock_request):
        """Test request retry with max retries exceeded."""
        mock_original_request = Mock()
        mock_original_request.method = 'GET'
        mock_original_request.url = 'https://api.example.com/test'
        mock_original_request.headers = {}
        mock_original_request.body = None
        
        # Mock all responses return 402
        mock_response = Mock()
        mock_response.status_code = 402
        mock_request.return_value = mock_response
        
        with pytest.raises(RuntimeError, match="Request still returned 402"):
            self.processor._retry_request_with_payment(mock_original_request, "0xabc123")
        
        # Should have made 3 attempts
        assert mock_request.call_count == 3


class TestDeferredPayments:
    """Test cases for deferred payment batching."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.mock_wallet = Mock(spec=WalletManager)
        self.mock_wallet.get_address.return_value = "0x742d35Cc6634C0532925a3b8D4C9db96C4b5Da5e"
        
        self.processor = PaymentProcessor(self.mock_wallet, self.temp_db.name)
        
        self.test_recipient = "0x8ba1f109551bD432803012645Hac136c5C1b5A5e"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_add_deferred_payment_success(self):
        """Test adding deferred payment successfully."""
        self.processor.add_deferred_payment(0.50, self.test_recipient, "test-tool")
        
        assert len(self.processor.deferred_payments) == 1
        payment = self.processor.deferred_payments[0]
        assert payment['amount'] == 0.50
        assert payment['recipient'] == self.test_recipient
        assert payment['tool_name'] == "test-tool"
    
    def test_add_deferred_payment_invalid_amount(self):
        """Test adding deferred payment with invalid amount."""
        with pytest.raises(ValueError, match="Payment amount must be positive"):
            self.processor.add_deferred_payment(-0.50, self.test_recipient, "test-tool")
    
    def test_add_deferred_payment_invalid_recipient(self):
        """Test adding deferred payment with invalid recipient."""
        with pytest.raises(ValueError, match="Invalid recipient address format"):
            self.processor.add_deferred_payment(0.50, "invalid_address", "test-tool")
    
    def test_add_deferred_payment_threshold_trigger(self):
        """Test automatic processing when threshold is reached."""
        # Mock successful batch processing
        self.mock_wallet.batch_payments.return_value = ["0xabc123"] * 10
        
        # Add 10 payments to trigger threshold
        for i in range(10):
            self.processor.add_deferred_payment(0.10, self.test_recipient, f"tool-{i}")
        
        # Should have triggered processing and cleared deferred payments
        assert len(self.processor.deferred_payments) == 0
        self.mock_wallet.batch_payments.assert_called_once()
    
    def test_process_deferred_payments_success(self):
        """Test successful processing of deferred payments."""
        # Add some deferred payments
        self.processor.add_deferred_payment(0.25, self.test_recipient, "tool1")
        self.processor.add_deferred_payment(0.75, self.test_recipient, "tool2")
        
        # Mock successful batch processing
        self.mock_wallet.batch_payments.return_value = ["0xabc123", "0xdef456"]
        
        result = self.processor.process_deferred_payments()
        
        assert result is True
        assert len(self.processor.deferred_payments) == 0
        self.mock_wallet.batch_payments.assert_called_once()
    
    def test_process_deferred_payments_empty_queue(self):
        """Test processing with empty deferred payment queue."""
        result = self.processor.process_deferred_payments()
        
        assert result is True
        self.mock_wallet.batch_payments.assert_not_called()
    
    def test_process_deferred_payments_partial_failure(self):
        """Test processing with some failed payments."""
        # Add deferred payments
        self.processor.add_deferred_payment(0.25, self.test_recipient, "tool1")
        self.processor.add_deferred_payment(0.75, self.test_recipient, "tool2")
        
        # Mock partial failure (one success, one failure)
        self.mock_wallet.batch_payments.return_value = ["0xabc123", "FAILED: Network error"]
        
        result = self.processor.process_deferred_payments()
        
        assert result is False  # Not all payments successful
        assert len(self.processor.deferred_payments) == 0  # Queue still cleared
    
    def test_process_deferred_payments_complete_failure(self):
        """Test processing with complete batch failure."""
        # Add deferred payments
        self.processor.add_deferred_payment(0.25, self.test_recipient, "tool1")
        
        # Mock batch processing failure
        self.mock_wallet.batch_payments.side_effect = RuntimeError("Network error")
        
        with pytest.raises(RuntimeError, match="Deferred payment processing failed"):
            self.processor.process_deferred_payments()
        
        # Queue should still be cleared
        assert len(self.processor.deferred_payments) == 0
    
    def test_force_process_deferred_payments(self):
        """Test manual processing trigger."""
        # Add some payments (below threshold)
        self.processor.add_deferred_payment(0.25, self.test_recipient, "tool1")
        
        # Mock successful processing
        self.mock_wallet.batch_payments.return_value = ["0xabc123"]
        
        result = self.processor.force_process_deferred_payments()
        
        assert result is True
        assert len(self.processor.deferred_payments) == 0
    
    def test_get_pending_payment_count(self):
        """Test getting pending payment count."""
        assert self.processor.get_pending_payment_count() == 0
        
        self.processor.add_deferred_payment(0.25, self.test_recipient, "tool1")
        assert self.processor.get_pending_payment_count() == 1
        
        self.processor.add_deferred_payment(0.50, self.test_recipient, "tool2")
        assert self.processor.get_pending_payment_count() == 2
    
    def test_get_pending_payment_total(self):
        """Test getting total pending payment amount."""
        assert self.processor.get_pending_payment_total() == 0.0
        
        self.processor.add_deferred_payment(0.25, self.test_recipient, "tool1")
        assert self.processor.get_pending_payment_total() == 0.25
        
        self.processor.add_deferred_payment(0.75, self.test_recipient, "tool2")
        assert self.processor.get_pending_payment_total() == 1.0


class TestPaymentLogging:
    """Test cases for payment logging and audit trail."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.mock_wallet = Mock(spec=WalletManager)
        self.mock_wallet.get_address.return_value = "0x742d35Cc6634C0532925a3b8D4C9db96C4b5Da5e"
        
        self.processor = PaymentProcessor(self.mock_wallet, self.temp_db.name)
        
        self.test_recipient = "0x8ba1f109551bD432803012645Hac136c5C1b5A5e"
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_log_payments_success(self):
        """Test successful payment logging."""
        payments = [
            Payment(0.50, self.test_recipient, "tool1", datetime.now(), "completed", "0xabc123"),
            Payment(0.25, self.test_recipient, "tool2", datetime.now(), "failed", "")
        ]
        
        self.processor._log_payments(payments)
        
        # Verify payments were logged to database
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM payment_transactions")
            count = cursor.fetchone()[0]
            assert count == 2
    
    def test_log_payments_empty_list(self):
        """Test logging empty payment list."""
        self.processor._log_payments([])
        
        # Should not raise error and database should remain empty
        with sqlite3.connect(self.temp_db.name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM payment_transactions")
            count = cursor.fetchone()[0]
            assert count == 0
    
    def test_get_payment_history_success(self):
        """Test retrieving payment history."""
        # Add some test payments to database
        payments = [
            Payment(0.50, self.test_recipient, "tool1", datetime.now(), "completed", "0xabc123"),
            Payment(0.25, self.test_recipient, "tool2", datetime.now() - timedelta(days=1), "completed", "0xdef456")
        ]
        self.processor._log_payments(payments)
        
        history = self.processor.get_payment_history()
        
        assert len(history) == 2
        assert history[0]['amount'] == 0.50
        assert history[1]['amount'] == 0.25
    
    def test_get_payment_history_with_filters(self):
        """Test retrieving payment history with filters."""
        # Add test payments
        payments = [
            Payment(0.50, self.test_recipient, "tool1", datetime.now(), "completed", "0xabc123"),
            Payment(0.25, self.test_recipient, "tool2", datetime.now(), "completed", "0xdef456")
        ]
        self.processor._log_payments(payments)
        
        # Filter by tool name
        history = self.processor.get_payment_history(tool_name="tool1")
        assert len(history) == 1
        assert history[0]['tool_name'] == "tool1"
        
        # Filter by agent ID
        agent_id = self.mock_wallet.get_address()
        history = self.processor.get_payment_history(agent_id=agent_id)
        assert len(history) == 2
    
    def test_get_payment_history_date_filter(self):
        """Test payment history with date filtering."""
        # Add old payment (beyond date range)
        old_payment = Payment(1.0, self.test_recipient, "old-tool", 
                            datetime.now() - timedelta(days=35), "completed", "0xold123")
        self.processor._log_payments([old_payment])
        
        # Add recent payment
        recent_payment = Payment(0.50, self.test_recipient, "new-tool", 
                               datetime.now(), "completed", "0xnew123")
        self.processor._log_payments([recent_payment])
        
        # Get history for last 30 days
        history = self.processor.get_payment_history(days=30)
        
        assert len(history) == 1
        assert history[0]['tool_name'] == "new-tool"
    
    def test_get_spending_analytics_success(self):
        """Test spending analytics generation."""
        # Add test payments
        payments = [
            Payment(0.50, self.test_recipient, "tool1", datetime.now(), "completed", "0xabc123"),
            Payment(0.25, self.test_recipient, "tool1", datetime.now(), "completed", "0xdef456"),
            Payment(0.75, self.test_recipient, "tool2", datetime.now(), "completed", "0xghi789")
        ]
        self.processor._log_payments(payments)
        
        analytics = self.processor.get_spending_analytics()
        
        assert analytics['total_spent'] == 1.50
        assert analytics['transaction_count'] == 3
        assert analytics['average_transaction'] == 0.50
        assert len(analytics['spending_by_tool']) == 2
        
        # Check tool spending breakdown
        tool_spending = {item['tool_name']: item['total_spent'] for item in analytics['spending_by_tool']}
        assert tool_spending['tool1'] == 0.75
        assert tool_spending['tool2'] == 0.75
    
    def test_get_spending_analytics_no_data(self):
        """Test spending analytics with no data."""
        analytics = self.processor.get_spending_analytics()
        
        assert analytics['total_spent'] == 0.0
        assert analytics['transaction_count'] == 0
        assert analytics['average_transaction'] == 0.0
        assert len(analytics['spending_by_tool']) == 0
        assert len(analytics['daily_spending']) == 0
    
    def test_get_spending_analytics_failed_payments_excluded(self):
        """Test that failed payments are excluded from analytics."""
        payments = [
            Payment(0.50, self.test_recipient, "tool1", datetime.now(), "completed", "0xabc123"),
            Payment(0.25, self.test_recipient, "tool2", datetime.now(), "failed", ""),
            Payment(0.75, self.test_recipient, "tool3", datetime.now(), "completed", "0xdef456")
        ]
        self.processor._log_payments(payments)
        
        analytics = self.processor.get_spending_analytics()
        
        # Should only count completed payments
        assert analytics['total_spent'] == 1.25
        assert analytics['transaction_count'] == 2