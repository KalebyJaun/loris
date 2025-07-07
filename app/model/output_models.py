from pydantic import BaseModel, Field
from typing import Optional, List


class PurchaseInfo(BaseModel):
    """Schema for purchase information extraction"""
    store_name: str = Field(
        description="Name of the store or establishment where the purchase was made",
        default="Unknown Store"
    )
    amount: float = Field(
        description="Total amount of the purchase (numeric value only)",
        default=0.0
    )
    currency: str = Field(
        description="Currency symbol or code (e.g., R$, $, €)",
        default="R$"
    )
    date: str = Field(
        description="Date of the purchase",
        default="Unknown Date"
    )
    payment_method: str = Field(
        description="Method of payment used (credit card, debit card, cash, etc.)",
        default="Unknown"
    )
    category: Optional[str] = Field(
        description="Category of purchase (e.g., groceries, utilities, entertainment)",
        default="Uncategorized"
    )
