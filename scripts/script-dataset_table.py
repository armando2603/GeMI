import pandas as pd
import json
from transformers import GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained('distilgpt2')
df = pd.read_csv('../frontend/src/assets/dataset.csv')
# load the json structure
dump_json = df.to_json(orient='values')
raw_json = json.loads(dump_json)
# create a new dict
dataset = []
for elem in raw_json:
    full_text = elem[1] + ' ' + elem[2]
    if len(tokenizer.encode(full_text)) < 240:
        # I use the GSM id as key in the json
        id = elem[0]
        input_split = elem[1].split(' = ')[0]
        input_split = input_split.split(' - Description')
        # handle the case there are more ' - '
        input_split[1] = ''.join(['Description', input_split[1]])
        tmp_split = input_split[1].split(' - Characteristics')
        # handle the case there is no Characteristics
        if len(tmp_split) == 1:
            tmp_split.append(':  ')
        input_split = [input_split[0], tmp_split[0], tmp_split[1]]
        input_split[2] = ''.join(['Characteristics', input_split[2]])
        input_split = [input_split[i].split(': ') for i in range(len(input_split))]
        # there are ' :' in the description text, so I join it
        for i in range(len(input_split)):
            if len(input_split[i]) > 1:
                input_split[i][1] = ': '.join(input_split[i][1:])
        # create the dict
        dataset.append(dict(
            id=id,
            title=input_split[0][1],
            description=input_split[1][1],
            characteristics=input_split[2][1]
        ))
# create the json file
with open('../frontend/src/assets/dataset_table.json', 'w') as json_file:
    json.dump(dataset, json_file)
print('json file created.')
