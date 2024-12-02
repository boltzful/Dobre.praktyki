import logging
from enum import Enum
from abc import ABC, abstractmethod

# logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Enums and result classes
class TransactionStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TransactionResult:
    def __init__(self, success: bool, transaction_id: str, message: str = ""):
        self.success = success
        self.transaction_id = transaction_id
        self.message = message

class NetworkException(Exception):
    pass

class PaymentException(Exception):
    pass

class RefundException(Exception):
    pass

# Abstract class for PaymentGateway
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, user_id: str, amount: float) -> TransactionResult:
        pass

    @abstractmethod
    def refund(self, transaction_id: str) -> TransactionResult:
        pass

    @abstractmethod
    def get_status(self, transaction_id: str) -> TransactionStatus:
        pass

# PaymentProcessor implementation
class PaymentProcessor:
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway

    def process_payment(self, user_id: str, amount: float) -> TransactionResult:
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number")
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty or whitespace")

        logger.info("Processing payment for user %s with amount %.2f", user_id, amount)
        try:
            result = self.payment_gateway.charge(user_id, amount)
            logger.info("Payment successful: %s", result.transaction_id)
            return result
        except (NetworkException, PaymentException) as e:
            logger.error("Payment failed for user %s: %s", user_id, str(e))
            return TransactionResult(success=False, transaction_id="", message=str(e))

    def refund_payment(self, transaction_id: str) -> TransactionResult:
        if not transaction_id or not transaction_id.strip():
            raise ValueError("Transaction ID cannot be empty or whitespace")

        logger.info("Processing refund for transaction %s", transaction_id)
        try:
            result = self.payment_gateway.refund(transaction_id)
            logger.info("Refund successful: %s", transaction_id)
            return result
        except (NetworkException, RefundException) as e:
            logger.error("Refund failed for transaction %s: %s", transaction_id, str(e))
            return TransactionResult(success=False, transaction_id="", message=str(e))

    def get_payment_status(self, transaction_id: str) -> TransactionStatus:
        if not transaction_id or not transaction_id.strip():
            raise ValueError("Transaction ID cannot be empty or whitespace")

        logger.info("Checking status for transaction %s", transaction_id)
        try:
            status = self.payment_gateway.get_status(transaction_id)
            logger.info("Transaction %s status: %s", transaction_id, status.value)
            return status
        except NetworkException as e:
            logger.error("Failed to retrieve status for transaction %s: %s", transaction_id, str(e))
            return TransactionStatus.FAILED
