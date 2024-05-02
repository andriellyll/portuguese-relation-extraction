import json

import typer
from pathlib import Path

from spacy.tokens import Span, DocBin, Doc
from spacy.vocab import Vocab
from wasabi import Printer

from spacy import blank
import numpy as np

msg = Printer()

SYMM_LABELS = ["PERSONAL_ADDRESS", "BIRTHDAY_DATE", "GENDER", "MEDICAL_INFO", "BIOMETRIC", "SEXUAL_INFO"]
MAP_LABELS = {
    "PERSONAL_ADDRESS": "PERSONAL_ADDRESS",
    "BIRTHDAY_DATE": "BIRTHDAY_DATE",
    "GENDER": "GENDER",
    "ETHNICITY": "ETHNICITY",
    "MEDICAL_INFO": "MEDICAL_INFO",
    "BIOMETRIC": "BIOMETRIC",
    "SEXUAL_INFO": "SEXUAL_INFO",
}

nlp = blank("pt")

def main(json_loc: Path, train_file: Path, dev_file: Path, test_file: Path):
    """Creating the corpus from the Prodigy annotations."""
    Doc.set_extension("rel", default={})
    vocab = Vocab()

    docs = {"train": [], "dev": [], "test": [], "total": []}
    ids = {"train": set(), "dev": set(), "test": set()}
    count_all = {"train": 0, "dev": 0, "test": 0,"total": 0}
    count_pos = {"train": 0, "dev": 0, "test": 0,"total": 0}

    
    with open(json_loc, encoding="utf8") as jsonfile:
        file = json.load(jsonfile)
        for example in file:

    # with json_loc.open("r", encoding="utf8") as jsonfile:
    #     for line in jsonfile:
            # example = json.loads(line)
            span_starts = set()
            # if example["answer"] == "accept":
            neg = 0
            pos = 0
            try:
                # Parse the tokens
                # words = [t["text"] for t in example["tokens"]]
                # spaces = [t["ws"] for t in example["tokens"]]
                # doc = Doc(vocab, words=words, spaces=spaces)
                tokens=nlp(example["document"])

                spaces=[]
                spaces = [True if tok.whitespace_ else False for tok in tokens]
                words = [t.text for t in tokens]
                doc = Doc(nlp.vocab, words=words, spaces=spaces)

                # Parse the GGP entities
                spans = example["tokens"]
                entities = []
                # span_start_token = {}
                for span in spans:
                    entity = doc.char_span(
                        int(span["start"]), int(span["end"]), label=span["entityLabel"]
                    )
                    # if (entity is None):
                    #     print(span)
                    # span_end_to_start[span["token_end"]] = span["token_start"]
                    entities.append(entity)
                    span_starts.add(int(span["token_start"]))
                    # span_start_token[span["token_start"]] = int(span["start"])
                doc.ents = [e for e in entities if e is not None]
                print(len(entities) != len(doc.ents))

                # Parse the relations
                rels = {}
                for x1 in span_starts:
                    for x2 in span_starts:
                        rels[(x1, x2)] = {}

                relations = example["relations"]

                for relation in relations:
                    # the 'head' and 'child' annotations refer to the end token in the span
                    # but we want the first token
                    # start = span_start_token[relation["head"]]
                    # end = span_start_token[relation["child"]]
                    start = int(relation["head"])
                    end = int(relation["child"])
                    label = relation["relationLabel"]
                    label = MAP_LABELS[label]
                    # para relações simultaneas, é anotado nas duas direções start -> end e end -> start
                    if label not in rels[(start, end)]:
                        rels[(start, end)][label] = 1.0
                        pos += 1
                    if label in SYMM_LABELS:
                        if label not in rels[(end, start)]:
                            rels[(end, start)][label] = 1.0
                            pos += 1

                # The annotation is complete, so fill in zero's where the data is missing
                for x1 in span_starts:
                    for x2 in span_starts:
                        for label in MAP_LABELS.values():
                            if label not in rels[(x1, x2)]:
                                neg += 1
                                rels[(x1, x2)][label] = 0.0
                doc._.rel = rels

                # only keeping documents with at least 1 positive case
                # if pos > 0:
                #     # use the original PMID/PMCID to decide on train/dev/test split
                #     # article_id = article_id.replace(".txt", "")
                #     article_id = example["documentName"].split(".")[0]
                #     if article_id.endswith("0") or article_id.endswith("5"):
                #         ids["dev"].add(article_id)
                #         docs["dev"].append(doc)
                #         count_pos["dev"] += pos
                #         count_all["dev"] += pos + neg
                #     elif article_id.endswith("3"):
                #         ids["test"].add(article_id)
                #         docs["test"].append(doc)
                #         count_pos["test"] += pos
                #         count_all["test"] += pos + neg
                #     else:
                #         ids["train"].add(article_id)
                #         docs["train"].append(doc)
                #         count_pos["train"] += pos
                #         count_all["train"] += pos + neg
                
                # only keeping documents with at least 1 positive case
                if pos > 0:
                        docs["total"].append(doc)
                        count_pos["total"] += pos
                        count_all["total"] += pos + neg

            except KeyError as e:
                msg.fail(f"Skipping doc because of key error: {e} ")

    total_docs = docs["total"]
    np.random.shuffle(total_docs)

    total_documentos = len(total_docs)
    tamanho_treino = int(total_documentos * 0.7)
    tamanho_teste = int(total_documentos * 0.15)

    documentos_treino = total_docs[:tamanho_treino]
    documentos_teste = total_docs[tamanho_treino:tamanho_treino+tamanho_teste]
    documentos_validacao = total_docs[tamanho_treino+tamanho_teste:]

    docbin = DocBin(docs=documentos_treino, store_user_data=True)
    docbin.to_disk(train_file)
    msg.info(
        f"{len(documentos_treino)} training sentences from {len(ids['train'])} articles, "
        f"{count_pos['train']}/{count_all['train']} pos instances."
    )

    docbin = DocBin(docs=documentos_validacao, store_user_data=True)
    docbin.to_disk(dev_file)
    msg.info(
        f"{len(documentos_validacao)} dev sentences from {len(ids['dev'])} articles, "
        f"{count_pos['dev']}/{count_all['dev']} pos instances."
    )

    docbin = DocBin(docs=documentos_teste, store_user_data=True)
    docbin.to_disk(test_file)
    msg.info(
        f"{len(documentos_teste)} test sentences from {len(ids['test'])} articles, "
        f"{count_pos['test']}/{count_all['test']} pos instances."
    )
    
    # docbin = DocBin(docs=docs["total"], store_user_data=True)
    # docbin.to_disk(train_file)
    # msg.info(
    #     # f"{len(docs['total'])} training sentences"
    #     "teste"
    # )


if __name__ == "__main__":
    typer.run(main)
