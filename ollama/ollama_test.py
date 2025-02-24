from ollama import Client

client = Client(host="http://localhost:7869")

response = client.chat(
            model="llama3.2-vision",
            messages=[
                {
                    'role': 'system',
                    'content': "ola"
                }
            ]
        )
print(response)
