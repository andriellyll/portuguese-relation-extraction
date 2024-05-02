import os
import time
from openai import OpenAI

# Instanciação do cliente openai
# client

for i in range(100):
    instrucao = """dê exemplo de Registro Médico que contém informações origem racial ou étnica, \
        questões genéticas, biométricas e sobre a saúde ou a vida sexual de uma pessoa, utilizando dados sintéticos. \
        o texto exemplo pode ser em formato de texto corrido ou de formulário. responda apenas com o exemplo pedido."""

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": instrucao,
            }
        ],
        model="gpt-3.5-turbo",
    )

    resposta = chat_completion.choices[0].message.content
    if (resposta is not None):
        f = open(f"data/gpt-3/example_{i}.txt", "w")
        f.write(resposta)
        f.close()
        
    time.sleep(60)
