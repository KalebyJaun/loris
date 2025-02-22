from pydantic import BaseModel, Field
from typing import Optional


class ComprovanteFinanceiro(BaseModel):
    valor: str = Field(..., description="The final purchase value, usually preceded by R$, U$")
    data_hora: str = Field(..., description="The exact moment of the transaction DD/MM/YYYY HH:MM:SS")
    meio_pagamento: str = Field(..., description="It can be credit for DEBITO or credito for CREDITO or pix for PIX")
    estabelecimento: str = Field(..., description="The name of the company where the purchase was made.")
    #cnpj: Optional[str] = Field(None, description="a sequence of characters as in the example 99.999.778/0001-11")
    #localizacao: str = Field(..., description="City and state where the purchase was made.")
