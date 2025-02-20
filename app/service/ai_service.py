from ollama import Client
from config import settings

from model.ai_models import ComprovanteFinanceiro

import os
os.environ["OLLAMA_DEBUG"] = "1"

class OllamaService():
    def __init__(self):
        self.client = Client(host=settings.ollama_host)
        self.vision_model = settings.ollama_vision_model

    def get_image_info(self, image_location: str) -> ComprovanteFinanceiro:
        SYSTEM_PROMPT = """Você é um assistente especializado em analisar comprovantes financeiros e extrair informações relevantes. Dado um comprovante em imagem, identifique e extraia os seguintes dados:
                    Valor da transação: O valor final da compra.
                    Moeda: A moeda utilizada na transação (exemplo: BRL, USD, EUR).
                    Categoria: A categoria do estabelecimento (mercado, escola, restaurante, lazer, construção, etc.).
                    Data e hora: O momento exato da transação.
                    Meio de pagamento: Se foi débito, crédito, PIX ou outro método.
                    Últimos dígitos do cartão: Caso o pagamento tenha sido com cartão, identifique os últimos quatro dígitos.
                    Nome do estabelecimento: O nome da empresa onde a compra foi feita.
                    CNPJ ou identificador fiscal: Caso disponível no comprovante, extraia o CNPJ ou outro número fiscal.
                    Localização: Cidade e estado onde a compra foi feita.
                    Número de autorização: Se disponível, extraia o código de autorização da transação.
                    Número do terminal: O identificador do terminal da máquina de pagamento."""
        
        response = self.client.chat(
            model=self.vision_model,
            format=ComprovanteFinanceiro.model_json_schema(),
            messages=[
                {
                    'role': 'system',
                    'content': SYSTEM_PROMPT
                },
                {
                    'role': 'user',
                    'content': 'Analise esse comprovante financeiro e me traga as informações contidas nele',
                    'images': [image_location],
                }
            ],
            options={'temperature': 0}
        )

        comprovante = ComprovanteFinanceiro.model_validate_json(response.message.content)
        return comprovante