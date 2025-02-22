from ollama import Client
from config import settings

from model.ai_models import ComprovanteFinanceiro

class OllamaTools():
    def __init__(self):
        self.client = Client(host=settings.ollama_host)
        self.vision_model = settings.ai_model

    def get_image_info(self, imaget_text: str) -> str:
        SYSTEM_PROMPT = """Voce é um assistente responsável por extrair informações de extratos bancários e comprovantes de pagamento ou transações financeiras
        as transaçoes devem ser retornadas como json com as transaçoes no formato:
        {
        "estabelecimento":"nome da onde foi feita a transaçao",
        "valor_transacao":"valor da transacao, pode ser precedido por R$ ou RG seguido de uma numero com duas casas decimais como 1829.23 ou 1829,23",
        "meio_pagamento":"meio usado para efetuar a transacao (credito, debito, pix procure por estas palavras no texto)",
        "data_hora":"hora da transaçao"
        }

        Se houver mais de uma transação retorne uma lista com todas elas
        """

        USER_PROMPT = f"""extraia as informaçoes do extrato bancario abaixo:
                    {imaget_text}
                    retorne um json com as transaçoes com as chaves abaixo:
                    
                    "estabelecimento":"nome da onde foi feita a transaçao",
                    "valor_transacao":"valor da transacao, pode ser precedido por R$ ou RG seguido de uma numero com duas casas decimais como 1829.23 ou 1829,23",
                    "meio_pagamento":"crédito, débito ou PIX somente esses valores são aceitos",
                    "data_hora":"hora da transaçao"
                    """
        
        # response = self.client.chat(
        #     model=self.vision_model,
        #     format=ComprovanteFinanceiro.model_json_schema(),
        #     messages=[
        #         {
        #             'role': 'system',
        #             'content': SYSTEM_PROMPT
        #         },
        #         {
        #             'role': 'user',
        #             'content': SYSTEM_PROMPT
        #         }
        #     ]
        # )
        
        response = self.client.generate(
            self.vision_model,
            USER_PROMPT
        )

        #return ComprovanteFinanceiro.model_validate_json(response.message.content)
        
        return response['response']
