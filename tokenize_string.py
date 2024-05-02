
from spacy import blank

nlp = blank("pt")

def tokenize_string(doc):
    text = doc.text
    tokens = [t for t in doc]

    last_found = 0

    # Cria um dicionário para armazenar os tokens
    token_dict = {}

    for token_number, token in enumerate(tokens):
        # Insere a posição inicial do token e o número do token no dicionário
        start_char = text.find(str(token), last_found)
        token_dict[start_char] = token_number

        last_found = start_char + 1

    return token_dict
