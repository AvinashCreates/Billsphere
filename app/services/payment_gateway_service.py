from dataclasses import dataclass
from uuid import uuid4


@dataclass
class PaymentGatewayResult:
    success: bool
    transaction_id: str
    payment_method: str
    amount: float
    message: str


class MockPaymentGateway:
    """
    Realistic mock payment gateway for development/testing.

    The customer does not choose success/failure directly.

    The gateway determines the result based on mock payment
    information, similar to how a real payment provider can
    approve or decline a transaction.
    """

    def process_payment(
        self,
        amount: float,
        payment_method: str = "card",
        payment_identifier: str | None = None,
    ) -> PaymentGatewayResult:

        transaction_id = f"MOCK-{uuid4()}"

        payment_method = payment_method.lower().strip()

        identifier = (
            payment_identifier.strip().lower()
            if payment_identifier
            else ""
        )

        # -----------------------------------------------------
        # UPI
        # -----------------------------------------------------
        if payment_method == "upi":

            if not identifier:
                return PaymentGatewayResult(
                    success=False,
                    transaction_id=transaction_id,
                    payment_method=payment_method,
                    amount=amount,
                    message="UPI payment declined: UPI ID is required.",
                )

            # Simulate invalid UPI format.
            if "@" not in identifier:
                return PaymentGatewayResult(
                    success=False,
                    transaction_id=transaction_id,
                    payment_method=payment_method,
                    amount=amount,
                    message="Payment declined: invalid UPI ID.",
                )

            # Simulate bank-side decline.
            if identifier in {
                "declined@mockupi",
                "failed@mockupi",
                "blocked@mockupi",
            }:
                return PaymentGatewayResult(
                    success=False,
                    transaction_id=transaction_id,
                    payment_method=payment_method,
                    amount=amount,
                    message="Payment declined by the bank.",
                )

            return PaymentGatewayResult(
                success=True,
                transaction_id=transaction_id,
                payment_method=payment_method,
                amount=amount,
                message="UPI payment processed successfully.",
            )

        # -----------------------------------------------------
        # CARD
        # -----------------------------------------------------
        if payment_method == "card":

            if not identifier:
                return PaymentGatewayResult(
                    success=False,
                    transaction_id=transaction_id,
                    payment_method=payment_method,
                    amount=amount,
                    message="Card payment declined: card details required.",
                )

            if identifier in {
                "4000000000000002",
                "declined",
                "failed",
                "declined@mockcardno.",
                "failed@mockcardno.",
            }:
                return PaymentGatewayResult(
                    success=False,
                    transaction_id=transaction_id,
                    payment_method=payment_method,
                    amount=amount,
                    message="Card payment declined by the issuer.",
                )

            return PaymentGatewayResult(
                success=True,
                transaction_id=transaction_id,
                payment_method=payment_method,
                amount=amount,
                message="Card payment processed successfully.",
            )

        # -----------------------------------------------------
        # BANK TRANSFER
        # -----------------------------------------------------
        if payment_method == "bank_transfer":

            if identifier in {
                "failed",
                "declined",
                "blocked",
                "declined@mockaccountno.",
                "failed@mockaccountno.",
            }:
                return PaymentGatewayResult(
                    success=False,
                    transaction_id=transaction_id,
                    payment_method=payment_method,
                    amount=amount,
                    message="Bank transfer declined by the bank.",
                )

            return PaymentGatewayResult(
                success=True,
                transaction_id=transaction_id,
                payment_method=payment_method,
                amount=amount,
                message="Bank transfer initiated successfully.",
            )

        # -----------------------------------------------------
        # Unsupported payment method
        # -----------------------------------------------------
        return PaymentGatewayResult(
            success=False,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=amount,
            message="Payment declined: unsupported payment method.",
        )


payment_gateway = MockPaymentGateway()

