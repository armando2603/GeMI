import pandas as pd
import json
from transformers import GPT2TokenizerFast

tokenizer = GPT2TokenizerFast.from_pretrained('distilgpt2')
df = pd.read_csv('../frontend/src/assets/dataset.csv')
# load the json structure
dump_json = df.to_json(orient='values')
raw_json = json.loads(dump_json)
# create a new dict
dataset = []
n_cut = 0
index = 0
for i, elem in enumerate(raw_json):
    if i == 20:
        break
    full_text = elem[1] + ' ' + elem[2]
    if len(tokenizer.encode(full_text)) < 200:
        # I use the GSM id as key in the json
        GSM = elem[0]
        # create the dict
        dataset.append(elem[1][:-3])
        index += 1
    else:
        n_cut += 1
# create the json file
print(f'{n_cut} samples have been cutted')
with open('input_list.json', 'w') as json_file:
    json.dump(dataset, json_file)
print('json file created.')
