import matplotlib.pyplot as plt
from pathlib import Path
import typer

# Função para ler o arquivo de texto e extrair os dados
def read_training_data(file_path):
    train_steps = []
    loss_transformer = []
    loss_relation_extractor = []
    rel_micro_precision = []
    rel_micro_recall = []
    rel_micro_f1 = []
    score = []

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith('E'):
                continue
            elif line.startswith('---'):
                continue
            elif line.strip() == '':
                continue
            elif line.startswith("#"):
                continue
            else:
                parts = line.split()
                train_steps.append(int(parts[1]))
                loss_transformer.append(float(parts[2]))
                loss_relation_extractor.append(float(parts[3]))
                rel_micro_precision.append(float(parts[4]))
                rel_micro_recall.append(float(parts[5]))
                rel_micro_f1.append(float(parts[6]))
                score.append(float(parts[7]))

    return train_steps, loss_transformer, loss_relation_extractor, rel_micro_precision, rel_micro_recall, rel_micro_f1, score

def main(file_path: Path):
    # Caminho do arquivo de texto
    # file_path = 'dados_de_treinamento.txt'

    print("teste")
    # Lendo os dados do arquivo
    train_steps, loss_transformer, loss_relation_extractor, rel_micro_precision, rel_micro_recall, rel_micro_f1, score = read_training_data(file_path)

    print(rel_micro_precision)
    # Plotando a curva de aprendizado
    plt.figure(figsize=(12, 8))

    # Losses
    plt.plot(train_steps, loss_transformer, label='Loss Transformer', marker='o')
    plt.plot(train_steps, loss_relation_extractor, label='Loss Relation Extractor', marker='o')

    # Micro Precision
    plt.plot(train_steps, rel_micro_precision, label='Rel Micro Precision', marker='o')

    # Micro Recall
    plt.plot(train_steps, rel_micro_recall, label='Rel Micro Recall', marker='o')

    # Micro F1 Score
    plt.plot(train_steps, rel_micro_f1, label='Rel Micro F1 Score', marker='o')

    # Score
    # plt.plot(train_steps, score, label='Score', marker='o')

    plt.title('Curva de Aprendizado')
    plt.xlabel('Passos de Treinamento')
    plt.ylabel('Valor')
    plt.legend()
    plt.grid(True)
    plt.savefig('my_plot.png')


if __name__ == "__main__":
    typer.run(main)
