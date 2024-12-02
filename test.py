import unittest
from unittest.mock import MagicMock
from program import PaymentProcessor, TransactionResult, TransactionStatus, NetworkException, RefundException

class TestPaymentProcessor(unittest.TestCase):
    def setUp(self):
        self.mock_gateway = MagicMock()
        self.processor = PaymentProcessor(self.mock_gateway)

    def test_process_payment_success(self):
        self.mock_gateway.charge.return_value = TransactionResult(True, "txn_12345", "Success")
        result = self.processor.process_payment("user_1", 100.0)
        self.mock_gateway.charge.assert_called_once_with("user_1", 100.0)
        self.assertTrue(result.success)
        self.assertEqual(result.transaction_id, "txn_12345")

    def test_process_payment_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.processor.process_payment("user_1", -50.0)

    def test_process_payment_empty_user_id(self):
        with self.assertRaises(ValueError):
            self.processor.process_payment("", 100.0)

    def test_process_payment_network_exception(self):
        self.mock_gateway.charge.side_effect = NetworkException("Network issue")
        result = self.processor.process_payment("user_1", 100.0)
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Network issue")

    def test_refund_payment_success(self):
        self.mock_gateway.refund.return_value = TransactionResult(True, "txn_12345", "Refunded")
        result = self.processor.refund_payment("txn_12345")
        self.mock_gateway.refund.assert_called_once_with("txn_12345")
        self.assertTrue(result.success)
        self.assertEqual(result.message, "Refunded")

    def test_refund_payment_invalid_transaction_id(self):
        with self.assertRaises(ValueError):
            self.processor.refund_payment("")

    def test_refund_payment_exception(self):
        self.mock_gateway.refund.side_effect = RefundException("Refund error")
        result = self.processor.refund_payment("txn_12345")
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Refund error")

    def test_get_payment_status_completed(self):
        self.mock_gateway.get_status.return_value = TransactionStatus.COMPLETED
        status = self.processor.get_payment_status("txn_12345")
        self.mock_gateway.get_status.assert_called_once_with("txn_12345")
        self.assertEqual(status, TransactionStatus.COMPLETED)

    def test_get_payment_status_invalid_transaction_id(self):
        with self.assertRaises(ValueError):
            self.processor.get_payment_status("")

    def test_get_payment_status_network_exception(self):
        self.mock_gateway.get_status.side_effect = NetworkException("Network issue")
        status = self.processor.get_payment_status("txn_12345")
        self.assertEqual(status, TransactionStatus.FAILED)

if __name__ == "__main__":
    unittest.main()
