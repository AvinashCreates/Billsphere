from pydantic import BaseModel

class WebhookPaymentPayload(BaseModel):
    gateway_reference: str
    status: str  # "succeeded" or "failed"