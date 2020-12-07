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
#     input_split = elem[1].split(' = ')[0]
#     input_split = input_split.split(' - Description')
#     # handle the case there are more ' - '
#     input_split[1] = ''.join(['Description', input_split[1]])
#     tmp_split = input_split[1].split(' - Characteristics')
#     # handle the case there is no Characteristics
#     if len(tmp_split) == 1:
#         tmp_split.append(':  ')
#     input_split = [input_split[0], tmp_split[0], tmp_split[1]]
#     input_split[2] = ''.join(['Characteristics', input_split[2]])
#     input_split = [input_split[i].split(': ') for i in range(len(input_split))]
#     # there are ' :' in the description text, so I join it  
#     for i in range(len(input_split)):
#         if len(input_split[i]) > 1:
#             input_split[i][1] = ': '.join(input_split[i][1:])
#     # create the dict
#     json_dict[id] = dict(
#         title=input_split[0][1],
#         description=input_split[1][1],
#         characteristics=input_split[2][1]
#     )
# create the json file
with open('../frontend/src/assets/dataset_table2.json', 'w') as json_file:
    json.dump(json_dict, json_file)
print('json file created.')
