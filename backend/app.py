from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from model import Predictor
from forked_lime.lime.lime_text import LimeTextExplainer
from GEOparse import get_GEO
import numpy as np
import json
import datetime
from os import path

# configuration
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)
pred = Predictor()


def gradientParser(
    output_indexes,
    data,
    output_ids,
    output_fields,
    confidences,
    input_ids
):
    output_split = []
    for i in range(len(output_indexes)):
        if output_indexes[i] == -1:
            output_split.append([output_fields[i], '<missing>'])
        else:
            if i < len(output_indexes) - 1:
                value = pred.tokenizer.decode(output_ids[
                    output_indexes[i]:output_indexes[i+1]-len(
                        pred.tokenizer.encode(output_fields[i+1])
                    )-2
                ])
                output_split.append([output_fields[i], value])
            else:
                value = pred.tokenizer.decode(output_ids[output_indexes[i]:-1])
                output_split.append([output_fields[i], value])

    # colors = ['red-3'] * 15 + ['orange-3'] * 8 + ['green-3'] * 3
    def get_color(i):
        if confidences[i] > 0.85:
            color = ['green-3']
        elif confidences[i] < 0.60:
            color = ['red-3']
        else:
            color = ['orange-3']
        return color

    outputs = [dict(
        field=elem[0],
        value=elem[1].strip(),
        color=get_color(i),
        fixed=False,
        confidence=np.round(np.float64(confidences[i]), 2)
        ) for i, elem in enumerate(output_split)]
    # gradient saliency
    gradient_score = pred.grad_explain

    input_tokens = pred.tokenizer.convert_ids_to_tokens(input_ids)
    input_tokens = list(
        map(
            pred.tokenizer.convert_tokens_to_string,
            input_tokens
        )
    )
    gradient_inputs = []
    for j in range(len(output_indexes)):
        if j < len(output_indexes) - 1:
            scores = gradient_score[
                output_indexes[j]: output_indexes[j+1]
                - len(pred.tokenizer.encode(output_fields[j+1]))
                - 2, :
            ]
        else:
            scores = gradient_score[
                output_indexes[j]:-1, :
            ]
        scores = np.mean(scores, axis=0)

        scores = scores[1:len(input_tokens)+1]
        max_scores = np.max(scores)
        max_scores = 1 if max_scores == 0.0 else max_scores
        scores = scores / max_scores
        assert len(input_tokens) == len(scores), (
            f'Gradient: len input_tokens {len(input_tokens)} != len scores {len(scores)}'
        )
        # print(len(scores))
        # print(len(input_tokens))
        # print(f'Il primo token è {input_tokens[-1]}')
        input_list = list(zip(input_tokens, scores))

        word_list = []
        values_list = input_list
        new_values_list = []
        i = 1
        while i < len(values_list):
            end_word = False
            mean_scores = [values_list[i-1][1]]
            new_world = values_list[i-1][0]
            while end_word is False:
                next_word = values_list[i][0]
                next_score = values_list[i][1]
                if (next_word[0] !=
                        (' ' or '_' or '-' or ':' or ';' or '(' or ')')):
                    new_world += next_word
                    mean_scores.append(next_score)
                else:
                    end_word = True
                    new_values_list.append(
                        [new_world, np.mean(mean_scores)]
                    )
                i += 1
                if i == len(values_list):
                    end_word = True
                    new_values_list.append(
                        [new_world, np.mean(mean_scores)]
                    )
        word_list.append(new_values_list)

        gradient_input = word_list
        for i, input_list in enumerate(gradient_input):
            for k, value in enumerate(input_list):
                opacity = np.int(np.ceil(value[1]*5)) if\
                    output_indexes[j] != -1 else 0
                bg_colors = f'bg-blue-{opacity}' if (
                    opacity) > 1 else 'bg-white'
                gradient_input[i][k][1] = bg_colors
            gradient_input[i] = [
                dict(
                    text=elem[0], color=elem[1]
                    ) for elem in gradient_input[i]
            ]
        gradient_inputs.append(gradient_input)
    return outputs, gradient_inputs


@app.route('/CallModel', methods=['POST'])
def CallModel():
    data = request.get_json()
    input_text = data['inputs'][0]['values'][0]['text']
    output_fields = data['output_fields']
    pred.fields = output_fields
    pred.model_id = data['exp_id']

    pred.predict([input_text])

    confidences = pred.confidences
    output_ids = pred.generated_sequence_ids
    output_indexes = np.array(pred.indexes)
    input_ids = np.array(pred.tokenizer.encode(input_text))

    outputs_1, gradient_inputs_1 = gradientParser(
        output_indexes,
        data,
        output_ids,
        output_fields,
        confidences,
        input_ids
    )

    output_fields = ['Cell Line', 'Tissue Type']
    pred.fields = output_fields
    pred.model_id = 1

    pred.predict([input_text])

    confidences = pred.confidences
    output_ids = pred.generated_sequence_ids
    output_indexes = np.array(pred.indexes)

    outputs_2, gradient_inputs_2 = gradientParser(
        output_indexes,
        data,
        output_ids,
        output_fields,
        confidences,
        input_ids
    )

    response = {
        'outputs': outputs_1 + outputs_2,
        # 'output_indexes': output_indexes.tolist(),
        'gradient': gradient_inputs_1 + gradient_inputs_2
    }
    return jsonify(response)


@app.route('/ComputeAttention', methods=['POST'])
def ComputeAttention():
    data = request.get_json()
    attentions = np.array(data['attentions'])
    inputs_data = data['inputs']
    output_fields = data['output_fields']
    # output_fields = [' ' + field for field in output_fields]
    output_indexes = np.array(data['output_indexes'])
    aggregationType = data['aggregation_type']
    selected_heads = np.array(data['selected_heads'])
    selected_layers = np.array(data['selected_layers'])
    heads_op = data['headsCustomOp']
    layers_op = data['layersCustomOp']
    input_text = inputs_data[0]['values'][0]['text']

    attention_inputs_list = AttentionParse(
        input_text,
        attentions,
        output_fields,
        output_indexes,
        aggregationType,
        selected_heads,
        selected_layers,
        heads_op,
        layers_op
    )

    response = {'attentions_results': attention_inputs_list}
    return jsonify(response)


@app.route('/Lime', methods=['POST'])
def Lime():
    data = request.get_json()
    inputs_data = data['inputs']
    input_text = inputs_data[0]['values'][0]['text'] + ' ='
    class_names = [pred.tokenizer.decode([x]) for x in range(len(pred.tokenizer))]
    explainer = LimeTextExplainer(class_names=class_names)
    pred.fields = [' ' + data['field']]
    pred.model_id = data['exp_id']
    exp = explainer.explain_instance(
        input_text, pred.predict, num_features=5, top_labels=1, num_samples=100
    )
    label = exp.available_labels()
    print(f'The top class is {pred.tokenizer.decode(list(label))}')
    weight_list = exp.as_list(label=label[0])
    result = [[], [], []]
    splits = [[inputs_data[i]["values"][0]["text"]] for i in range(len(inputs_data))]
    # print(weight_list)
    max_scores = {'negative': 0, 'positive': 0}
    for (word, score) in weight_list:
        if score > 0:
            if score > max_scores['positive']:
                max_scores['positive'] = score
        else:
            if abs(score) > max_scores['negative']:
                max_scores['negative'] = abs(score)
        for i in range(len(inputs_data)):
            new_split = []
            # print(splits[i])
            for element in splits[i]:
                split_word = element.split(word)
                if len(split_word) > 1:
                    for k, part in enumerate(split_word):
                        if k == (len(split_word) - 1):
                            new_split.append(part)
                        else:
                            new_split.append(part)
                            new_split.append(word)
                else:
                    new_split.append(element)
            splits[i] = new_split
    words = [element[0] for element in weight_list]
    # print(splits[0])
    for i, split in enumerate(splits):
        for element in split:
            score_element = weight_list[words.index(element)][1]\
                if element in words else 0
            if score_element != 0:
                if score_element > 0:
                    sign = 'positive'
                    color = 'green'
                else:
                    sign = 'negative'
                    color = 'red'
                # print(np.ceil(abs((score_element) / max_scores[sign])*5))
                opacity = int(np.ceil(abs((score_element) / max_scores[sign])*5))\
                    if max_scores[sign] > 0 else int(np.ceil(score_element))
                result[i].append(
                    dict(text=element, color=f'bg-{color}-{opacity}')
                )
            else:
                result[i].append(dict(text=element, color='bg-white'))
    return jsonify(result)


@app.route('/getJSONs', methods=['GET'])
def getJSONs():
    if path.isfile('data/table_2.json') and path.isfile('data/table_2.json'):
        with open('data/table_1.json') as f:
            table_1 = json.load(f)
        with open('data/table_2.json') as f:
            table_2 = json.load(f)
    else:
        table_2 = []
        table_1 = []
        with open('data/table_2.json', 'w') as f:
            json.dump(table_2, f)
        with open('data/table_1.json', 'w') as f:
            json.dump(table_1, f)

    return jsonify([table_1, table_2])


@app.route('/storeJSON', methods=['POST'])
def storeJSON():
    data = request.get_json()
    if data['table_id'] == 1:
        with open('data/table_1.json', 'w') as f:
            json.dump(data['table'], f)
    elif data['table_id'] == 2:
        with open('data/table_2.json', 'w') as f:
            json.dump(data['table'], f)
    return 'ok'


@app.route('/uploader', methods=['POST'])
@cross_origin()
def upload():
    dataset_type = request.headers['Dataset']
    for fname in request.files:
        f = request.files.get(fname)
        f.save('data/input_' + dataset_type + '.json')
    return 'Okay!'


@app.route('/uploadTable', methods=['POST'])
@cross_origin()
def uploadTable():
    for fname in request.files:
        f = request.files.get(fname)
        f.save('data/table_2.json')
    return 'Okay!'


@app.route('/deleteTable', methods=['POST'])
@cross_origin()
def deleteTable():
    data = request.get_json()
    dataset_type = str(data['table_id'])
    with open('data/table_' + dataset_type + '.json', 'w') as file:
        json.dump([], file)
    return 'Okay!'


@app.route('/writeLog', methods=['POST'])
def writeLog():
    data = request.get_json()
    if data['editType'] == 'confirm' or data['editType'] == 'unknown':
        new_line = str(datetime.datetime.now()) + ', '
        new_line += 'GSM: ' + data['GSM'] + ', '
        new_line += 'edit type: ' + data['editType'] + ', '
        new_line += 'field: ' + data['field'] + ', '
        new_line += 'prediction: ' + data['prediction'] + ', '
        new_line += 'input text: ' + data['input_text']
    elif data['editType'] == 'new':
        new_line = str(datetime.datetime.now()) + ', '
        new_line += 'GSM: ' + data['GSM'] + ', '
        new_line += 'edit type: ' + data['editType'] + ', '
        new_line += 'field: ' + data['field'] + ', '
        new_line += 'prediction: ' + data['prediction'] + ', '
        new_line += 'edit text: ' + data['edit_text'] + ', '
        new_line += 'input text: ' + data['input_text']
    with open('data/editLog.txt', 'a') as log:
        log.write('\n')
        log.write(new_line)
    return 'Okay!'


@app.route('/generateTable', methods=['POST'])
def generateTable():
    data = request.get_json()
    output_fields = data['output_fields']
    input_data = data['data']

    input_list = []
    for gsm in input_data:

        input_text = '[gse]: ' + ' - '.join(gsm['GSE'])
        input_text += ' [title]: ' + gsm['title']
        input_text += ' [sample type]: ' + gsm['sample_type']
        input_text += ' [source name]: ' + gsm['source_name']
        input_text += ' [organism]: ' + gsm['organism']
        input_text += ' [characteristics]: ' + gsm['characteristics']
        input_text += ' [description]: ' + gsm['description']

        input_text = input_text.replace('_', ' ').replace('*', '')
        input_text_words = input_text.split(' ')
        input_text_words = [
            word if len(word) < 30 else '' for word in input_text_words
        ]
        input_text = ' '.join(input_text_words)


        # text_list = [
        #     # gsm['organism'],
        #     gsm['characteristics'],
        #     gsm['description'],
        #     gsm['title'],
        #     gsm['source_name'],
        #     # gsm['sample_type'],
        # ]

        # input_text = ' '.join(text_list) + ' ='
        # input_text_words = input_text.split(' ')
        # input_text_words = [
        #     word if len(word) < 30 else '' for word in input_text_words
        # ]
        # input_text_words = [
        #     word if set(word) != {'*'} else '' for word in input_text_words
        # ]
        # input_text = ' '.join(input_text_words)
        input_dict = dict(GSE=gsm['GSE'], GSM=gsm['GSM'], input_text=input_text)
        input_list.append(input_dict)

    dataset_type = str(data['exp_id'])
    pred.fields = [field for field in output_fields]
    pred.model_id = data['exp_id']
    # with open('data/input_' + dataset_type + '.json') as f:
    #     input_list = json.load(f)
    # input_list = [text + ' =' for text in input_list]
    new_table_json = pred.generateTable(input_list)

    with open('data/table_' + dataset_type + '.json', 'r') as file:
        actual_table = json.load(file)

    curr_id = len(actual_table)
    for i, elem in enumerate(new_table_json):
        new_table_json[i]['id'] = curr_id
        curr_id += 1
    # print(actual_table + new_table_json)
    with open('data/table_' + dataset_type + '.json', 'w') as file:
        json.dump(actual_table + new_table_json, file)
    return 'Okay!'


@app.route('/searchGEO', methods=['POST'])
def searchGEO():
    data = request.get_json()
    search_list = data['searchList']

    GEO_table = []
    for geo in search_list:
        if 'GSM' in geo:
            gsm = geo
            gsm = gsm.replace('"', '')
            gsm_data = get_GEO(geo=gsm, destdir='data/GEO')
            description = (
                ' - '.join(gsm_data.metadata['description'])
                if 'description' in gsm_data.metadata.keys()
                else ''
            )
            title = (
                ' - '.join(gsm_data.metadata['title'])
                if 'title' in gsm_data.metadata.keys()
                else ''
            )
            sample_type = (
                ' - '.join(gsm_data.metadata['type'])
                if 'type' in gsm_data.metadata.keys()
                else ''
            )
            source_name = (
                ' - '.join(gsm_data.metadata['source_name_ch1'])
                if 'source_name_ch1' in gsm_data.metadata.keys()
                else ''
            )
            organism = (
                ' - '.join(gsm_data.metadata['organism_ch1'])
                if 'organism_ch1' in gsm_data.metadata.keys()
                else ''
            )
            characteristics = (
                ' - '.join(gsm_data.metadata['characteristics_ch1'])
                if 'characteristics_ch1' in gsm_data.metadata.keys()
                else ''
            )
            GEO_table.append(
                dict(
                    GSM=gsm,
                    GSE=gsm_data.metadata['series_id'],
                    title=title,
                    sample_type=sample_type,
                    source_name=source_name,
                    organism=organism,
                    characteristics=characteristics,
                    description=description,
                )
            )
        if 'GSE' in geo:
            gse = geo
            gse_data = get_GEO(geo=gse, destdir='data/GEO')

            for gsm in gse_data.metadata['sample_id']:
                gsm_data = gse_data.gsms[gsm]
                description = (
                    ' - '.join(gsm_data.metadata['description'])
                    if 'description' in gsm_data.metadata.keys()
                    else ''
                )
                title = (
                    ' - '.join(gsm_data.metadata['title'])
                    if 'title' in gsm_data.metadata.keys()
                    else ''
                )
                sample_type = (
                    ' - '.join(gsm_data.metadata['type'])
                    if 'type' in gsm_data.metadata.keys()
                    else ''
                )
                source_name = (
                    ' - '.join(gsm_data.metadata['source_name_ch1'])
                    if 'source_name_ch1' in gsm_data.metadata.keys()
                    else ''
                )
                organism = (
                    ' - '.join(gsm_data.metadata['organism_ch1'])
                    if 'organism_ch1' in gsm_data.metadata.keys()
                    else ''
                )
                characteristics = (
                    ' - '.join(gsm_data.metadata['characteristics_ch1'])
                    if 'characteristics_ch1' in gsm_data.metadata.keys()
                    else ''
                )
                GEO_table.append(
                    dict(
                        GSM=gsm,
                        GSE=gsm_data.metadata['series_id'],
                        title=title,
                        sample_type=sample_type,
                        source_name=source_name,
                        organism=organism,
                        characteristics=characteristics,
                        description=description,
                    )
                )

    return jsonify(GEO_table)


def AttentionParse(
    input_text,
    attentions,
    output_fields,
    output_indexes,
    aggregationType,
    selected_heads,
    selected_layers,
    heads_op,
    layers_op
):
    attentions_list = []
    if aggregationType == 'custom':
        if selected_heads.shape[0] == 0 or selected_layers.shape[0] == 0:
            attentions_custom = np.zeros(
                [attentions.shape[-2], attentions.shape[-1]]
            )
        else:
            assert heads_op in ['avg', 'mul'], 'heads_op must be "mul" or "avg"'
            assert layers_op in ['avg', 'mul'], 'layer ops must be "mul" or "avg"'

            if heads_op == 'avg':
                attentions_custom = np.mean(attentions[:, selected_heads], 1)
                print('heads avg')
            else:
                attentions_custom = np.multiply.reduce(
                    attentions[:, selected_heads], 1
                )
                print('heads mul')

            if layers_op == 'avg':
                attentions_custom = np.mean(attentions_custom[selected_layers], 0)
                print('layer avg')
            else:
                attentions_custom = np.multiply.reduce(
                    attentions_custom[selected_layers], 0
                )
                print('layer mul')
        attentions_list.append(attentions_custom)
    else:
        attentions_1 = np.mean(attentions[-1, :], axis=0)
        attentions_list.append(attentions_1)
        attentions_2 = np.mean(np.mean(attentions, 1), axis=0)
        attentions_list.append(attentions_2)
        attentions_3 = np.multiply.reduce(np.mean(attentions, 1), axis=0)
        attentions_list.append(attentions_3)
        if selected_heads.shape[0] == 0 or selected_layers.shape[0] == 0:
            attentions_custom = np.zeros(
                [attentions.shape[-2], attentions.shape[-1]]
            )
        else:
            attentions_custom = np.mean(
                np.mean(attentions[:, selected_heads], 1)[selected_layers], 0
            )
        attentions_list.append(attentions_custom)
    # attentions_4 = np.mean(np.mean(attentions, 0), 0)
    # attentions_list.append(attentions_4)
    input_ids = np.array(pred.tokenizer.encode(input_text))
    # input_fields = [' ' + element['field'] for element in inputs_data]
    # values_indexes = []
    # for field in input_fields:
    #     field_ids = np.array(pred.tokenizer.encode(field))
    #     input_ids = np.array(pred.tokenizer.encode(input_text))
    #     indexes = np.ones(
    #         len(np.where(
    #             input_ids == field_ids[0])[0])
    #     ) * -1
    #     for i, field_id in enumerate(field_ids):
    #         current_indexes = np.where(
    #             input_ids == field_id)[0]
    #         for n, index in enumerate(indexes):
    #             if i == 0:
    #                 indexes = current_indexes
    #             else:
    #                 for current_index in current_indexes:
    #                     if index + 1 == current_index:
    #                         indexes[n] = current_index
    #                         break
    #                     else:
    #                         indexes[n] = -1

    #     if (len(np.where(indexes != -1)[0]) == 0):
    #         index = -1
    #     else:
    #         index = indexes[np.where(indexes != 1)[0][0]] + 2

    #     values_indexes.append(index)

    # print(values_indexes)
    input_tokens = pred.tokenizer.convert_ids_to_tokens(input_ids)
    input_tokens = list(
        map(
            pred.tokenizer.convert_tokens_to_string,
            input_tokens
        )
    )
    attention_inputs_list = []
    for attentions in attentions_list:
        attention_inputs = []
        for j in range(len(output_indexes)):
            if j < len(output_indexes) - 1:
                scores = attentions[
                    output_indexes[j]: output_indexes[j+1]
                    - len(pred.tokenizer.encode(output_fields[j+1]))
                    - 2, :
                ]
            else:
                scores = attentions[
                    output_indexes[j]:, :
                ]
            scores = np.mean(scores, axis=0)
            # print(f'per il field {output_fields[j]} index: {output_indexes[j]}')
    #         filtered_scores = []

    #         for i in range(len(values_indexes)):
    #             if i < len(values_indexes) - 1:
    #                 filtered_scores += list(scores[
    #                     values_indexes[i]:values_indexes[i+1]-len(
    #                         pred.tokenizer.encode(output_fields[i+1])
    #                     )-1
    #                 ])
    #             else:
    #                 filtered_scores += list(scores[values_indexes[i]:-1])
            scores[0] = 0
            max_scores = np.max(scores)
            # print(scores)
            max_scores = 1 if max_scores == 0.0 else max_scores
            scores = scores / max_scores
            # print(f'{output_fields[j]}')
            # print(scores)

            input_list = list(zip(input_tokens, scores))
            attention_input = []

            # for i in range(len(values_indexes)):
            #     if i < len(values_indexes) - 1:
            #         attention_input.append(input_list[
            #             values_indexes[i]:values_indexes[i+1]-len(
            #                 pred.tokenizer.encode(output_fields[i+1])
            #             )-1
            #         ])
            #     else:
            #         attention_input.append(input_list[values_indexes[i]:-1])
            new_attention_input = []
            values_list = input_list
            new_values_list = []
            i = 1
            while i < len(values_list):
                end_word = False
                mean_scores = [values_list[i-1][1]]
                new_world = values_list[i-1][0]
                while end_word is False:
                    next_word = values_list[i][0]
                    next_score = values_list[i][1]
                    if (next_word[0] !=
                            (' ' or '_' or '-' or ':' or ';' or '(' or ')')):
                        new_world += next_word
                        mean_scores.append(next_score)
                    else:
                        end_word = True
                        new_values_list.append(
                            [new_world, np.mean(mean_scores)]
                        )
                    i += 1
                    if i == len(values_list):
                        end_word = True
                        new_values_list.append(
                            [new_world, np.mean(mean_scores)]
                        )
            new_attention_input.append(new_values_list)
            attention_input = new_attention_input
            for i, input_list in enumerate(attention_input):
                for k, value in enumerate(input_list):
                    opacity = np.int(np.ceil(value[1]*5)) if\
                        output_indexes[j] != -1 else 0
                    bg_colors = f'bg-blue-{opacity}' if (
                        opacity) > 1 else 'bg-white'
                    attention_input[i][k][1] = bg_colors
                attention_input[i] = [
                    dict(
                        text=elem[0], color=elem[1]
                        ) for elem in attention_input[i]
                ]
            attention_inputs.append(attention_input)
        attention_inputs_list.append(attention_inputs)
    return attention_inputs_list


@app.route('/saveAndTrain', methods=['POST'])
def saveAndTrain():
    data = request.get_json()
    for index in [1, 2]:
        pred.model_id = index
        input_text = data['input_text']
        output_text = data['output_text'][str(index)]
        pred.onlineLearning(input_text, output_text)
    return 'okay'


@app.route('/regenerateTable', methods=['POST'])
def regenerateTable():
    data = request.get_json()
    input_list = data['inputList']
    pred.fields = data['output_fields']
    pred.model_id = data['exp_id']
    new_table_json = pred.generateTable(input_list)
    return jsonify(new_table_json)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--colab",
        action="store_true",
        help="colab mode"
    )
    args = parser.parse_args()
    if args.colab:
        from flask_ngrok import run_with_ngrok
        run_with_ngrok(app)
    app.run()
