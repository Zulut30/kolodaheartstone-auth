from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class InvoiceRequest:
    amount: Decimal
    currency: str
    description: str
    user_id: int
    order_id: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class InvoiceResult:
    provider: str
    external_id: str
    pay_url: str | None
    raw: dict[str, Any]


class PaymentProvider(ABC):
    name: str

    @abstractmethod
    async def create_invoice(self, req: InvoiceRequest) -> InvoiceResult: ...
