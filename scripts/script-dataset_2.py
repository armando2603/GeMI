import pandas as pd
import json

df = pd.read_csv('../frontend/src/assets/dataset2.csv')
# load the json structure
dump_json = df.to_json(orient='values')
raw_json = json.loads(dump_json)
print(raw_json[:5])
# create a new dict
json_dict = []
for i, elem in enumerate(raw_json):
    gsm_id = elem[1]
    gse_id = elem[2]
    input_text = elem[3]
    json_dict.append(dict(id=i, GSM=gsm_id, GSE=gse_id, text=input_text[:-3]))

#     )
# create the json file
with open('../frontend/src/assets/dataset_table2.json', 'w') as json_file:
    json.dump(json_dict, json_file)
print('json file created.')
