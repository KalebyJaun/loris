import openai
import json

from config import settings

import openai
import json
from config import settings

class OpenaiTools:
    def __init__(self):
        self.api_key = settings.open_ai_api_key
        self.model = settings.ai_model
        self.client = openai.OpenAI(api_key=self.api_key)

    def get_image_info(self, text: str) -> dict:
        prompt = (
            "Extraia as transações do extrato bancário abaixo e retorne um JSON no seguinte formato: "
            "{\"estabelecimento\":\"nome da onde foi feita a transação\", \"valor_transacao\":\"valor da transação, pode ser precedido por R$ ou RG seguido de um número com duas casas decimais como 1829.23 ou 1829,23\", "
            "\"meio_pagamento\":\"meio usado para efetuar a transação (crédito, débito, pix)\", \"data_hora\":\"hora da transação\"}. "
            "Texto: " + text
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

        