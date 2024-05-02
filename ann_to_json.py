import json
import glob, os
from tokenize_string import tokenize_string

from spacy import blank

nlp = blank("pt")

os.chdir("/home/andrielly/Documentos/tcc/data/all_files")
# annotation_file = 'example_0.ann'
documents = []
for annotation_file in glob.glob("*.ann"):
    try:
        with open(annotation_file) as file:
            entities = {}
            relations = []
            
            text_file = annotation_file.replace(".ann", ".txt")
            f = open(text_file, "r")
            file_content = f.read()

            token_dict = tokenize_string(nlp(file_content))

            for line in file.readlines():
                type, ann, text = line.split('\t')

                if (type.startswith('T')):
                    span_length = len(text.split(' '))
                    label, start, end = ann.split(' ')
                    start = int(start)
                    end = int(end)
                    entities[type] = {
                        "text": text.replace('\n', ''),
                        "start": start,
                        "end": end,
                        "token_start": token_dict[start],
                        "token_end": token_dict[start] + span_length - 1,
                        "entityLabel": label
                    }
                elif (type.startswith('R')):
                    label, arg1, arg2 = ann.split(' ')
                    arg1 = arg1.split(':')[-1]
                    arg2 = arg2.split(':')[-1]
                    rel = {
                        "head": entities[arg1]['token_start'],
                        "child": entities[arg2]['token_start'],
                        "relationLabel": label
                    }

                    relations.append(rel)

            document = {
                "documentName": text_file,
                "document": file_content,
                "tokens": list(entities.values()),
                "relations": relations
            }

            documents.append(document)
    except:
        print('porra')

with open("json_annotation.json", "w", encoding='utf8') as outfile: 
    json.dump(documents, outfile, ensure_ascii=False)