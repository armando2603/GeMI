import pandas as pd
import json
from transformers import GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
df = pd.read_csv('../frontend/src/assets/dataset2.csv')
# load the json structure
dump_json = df.to_json(orient='values')
raw_json = json.loads(dump_json)
# create a new dict
json_dict = []
index = 0
for elem in raw_json:
    full_text = elem[3] + ' ' + elem[4]
    if len(tokenizer.encode(full_text)) < 240:
        gsm_id = elem[1]
        gse_id = elem[2]
        input_text = elem[3]
        json_dict.append(dict(id=index, GSM=gsm_id, GSE=gse_id, text=input_text[:-3]))
        index += 1

# create the json file
with open('../frontend/src/assets/dataset_table2.json', 'w') as json_file:
    json.dump(json_dict, json_file)
print('json file created.')
