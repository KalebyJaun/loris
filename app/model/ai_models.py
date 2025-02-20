from pydantic import BaseModel, Field
from typing import Optional


class ComprovanteFinanceiro(BaseModel):
    valor: float = Field(..., description="Valor da transação")
    moeda: str = Field(..., description="Moeda utilizada na transação, ex: BRL, USD")
    categoria: str = Field(..., description="Categoria do estabelecimento, ex: Mercado, Restaurante")
    data_hora: str = Field(..., description="Data e hora da transação no formato DD/MM/YYYY HH:MM:SS")
    meio_pagamento: str = Field(..., description="Meio de pagamento utilizado, ex: Débito, Crédito, PIX")
    ultimos_digitos_cartao: Optional[str] = Field(None, description="Últimos quatro dígitos do cartão, se aplicável")
    estabelecimento: str = Field(..., description="Nome do estabelecimento")
    cnpj: Optional[str] = Field(None, description="CNPJ ou identificador fiscal do estabelecimento, se disponível")
    localizacao: str = Field(..., description="Cidade e estado onde a compra foi feita")
    numero_autorizacao: Optional[str] = Field(None, description="Número de autorização da transação, se disponível")
    numero_terminal: Optional[str] = Field(None, description="Número do terminal da máquina de pagamento")
