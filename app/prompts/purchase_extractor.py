from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
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
    items: Optional[List[str]] = Field(
        description="List of items purchased, if available",
        default_factory=list
    )
    category: Optional[str] = Field(
        description="Category of purchase (e.g., groceries, utilities, entertainment)",
        default="Uncategorized"
    )
    tax_amount: Optional[float] = Field(
        description="Tax amount if available",
        default=0.0
    )
    discount: Optional[float] = Field(
        description="Discount amount if available",
        default=0.0
    )

# Create the output parser
parser = PydanticOutputParser(pydantic_object=PurchaseInfo)

# Create the prompt template
purchase_extractor_template = """
You are a specialized assistant that extracts purchase information from receipts, invoices, and financial documents.
Your task is to carefully analyze the text and extract all relevant purchase information.

IMPORTANT: You must provide values for all required fields. If a field is not found in the text:
- For store_name, look for business names, store names, or merchant names
- For amount, look for total amounts, final values, or payment amounts
- For currency, look for currency symbols (R$, $, €) or currency codes
- For date, look for dates in any format and convert to YYYY-MM-DD
- For payment_method, look for payment type indicators (credit, debit, cash, PIX)
- For optional fields, use empty list [] or 0.0 as appropriate

{format_instructions}

Text to analyze:
{text}

Remember:
1. NEVER return null values for required fields
2. For amounts:
   - Look for values with currency symbols (R$, $, €)
   - Extract only the numeric value
   - Look for "Total", "Valor Total", "Amount", "Final Value"
3. For dates:
   - Look for dates in any format (DD/MM/YYYY, MM/DD/YYYY, etc.)
   - Convert to YYYY-MM-DD format
   - Look for "Data", "Date", "Emissão", "Issue Date"
4. For store names:
   - Look for business names at the top of receipts
   - Look for merchant names
   - Look for establishment names
5. For payment methods:
   - Look for "Cartão de Crédito", "Cartão de Débito", "Credit Card", "Debit Card"
   - Look for "PIX", "Dinheiro", "Cash"
6. If you can't find a value, use the default values specified above
7. Be thorough in your analysis - receipts often have information in different formats

JSON Output:
"""

# Create the prompt template
purchase_extractor_prompt = PromptTemplate(
    template=purchase_extractor_template,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

def get_purchase_extractor_prompt() -> PromptTemplate:
    """Get the purchase extractor prompt template"""
    return purchase_extractor_prompt

def get_purchase_parser() -> PydanticOutputParser:
    """Get the purchase information parser"""
    return parser 