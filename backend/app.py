from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from model import Predictor
from forked_lime.lime.lime_text import LimeTextExplainer
import numpy as np
import json

# configuration
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)
pred = Predictor()


@app.route('/CallModel', methods=['POST'])
def CallModel():
    data = request.get_json()
    inputs_data = data['inputs']
    # for element in inputs_data:
    #     input_text += f'{element["field"]}: {element["values"][0]["text"]} - '
    # input_text = input_text[:-2] + '='
    # if data['exp_id'] == 1:
    #     for element in inputs_data:
    #         input_text += f'{element["field"]}: {element["values"][0]["text"]} - '
    #         input_text = input_text[:-2] + '='
    # elif data['exp_id'] == 2:
    input_text = inputs_data[0]['values'][0]['text'] + ' ='
    inputs_ids_all = pred.tokenizer.encode(input_text)
    output_fields = data['output_fields']
    pred.fields = [' ' + field for field in output_fields]
    output_fields = [' ' + field for field in output_fields]
    pred.model_id = data['exp_id']
    # print(input_text)
    pred.predict([input_text])
    input_text = input_text = inputs_data[0]['values'][0]['text']
    confidences = pred.confidences
    output_ids = pred.generated_sequence_ids
    output_indexes = np.array(pred.indexes)
    input_ids = np.array(pred.tokenizer.encode(input_text))

    output_split = []
    for i in range(len(output_indexes)):
        if output_indexes[i] == -1:
            output_split.append([data['output_fields'][i], '<missing>'])
        else:
            if i < len(output_indexes) - 1:
                value = pred.tokenizer.decode(output_ids[
                    output_indexes[i]:output_indexes[i+1]-len(
                        pred.tokenizer.encode(output_fields[i+1])
                    )-2
                ])
                output_split.append([data['output_fields'][i], value])
            else:
                value = pred.tokenizer.decode(output_ids[output_indexes[i]:-1])
                output_split.append([data['output_fields'][i], value])

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
        value=elem[1],
        color=get_color(i) if (
            elem[1] != ' unknown' and elem[1] != ' None' and elem[1] != '<missing>'
            ) else 'grey-3',
        confidence=np.round(np.float64(confidences[i]), 2)
        ) for i, elem in enumerate(output_split)]
    # gradient saliency
    gradient_score = pred.grad_explain

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

        # filtered_scores = []

        # for i in range(len(values_indexes)):
        #     if i < len(values_indexes) - 1:
        #         filtered_scores += list(scores[
        #             values_indexes[i]:values_indexes[i+1]-len(
        #                 pred.tokenizer.encode(output_fields[i+1])
        #             )-1
        #         ])
        #     else:
        #         filtered_scores += list(scores[values_indexes[i]:-1])
        scores = scores[:len(input_tokens)]
        max_scores = np.max(scores)
        max_scores = 1 if max_scores == 0.0 else max_scores
        scores = scores / max_scores
        input_list = list(zip(input_tokens, scores))

        # for i in range(len(values_indexes)):
        #     if i < len(values_indexes) - 1:
        #         gradient_input.append(input_list[
        #             values_indexes[i]:values_indexes[i+1]-len(
        #                 pred.tokenizer.encode(output_fields[i+1])
        #             )-1
        #         ])
        #     else:
        #         gradient_input.append(input_list[values_indexes[i]:-1])
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
    response = {
        'outputs': outputs,
        'attentions': np.round(pred.attentions[
            :, :, len(inputs_ids_all):, :len(input_ids)
        ], 6).tolist(),
        'output_indexes': output_indexes.tolist(),
        'gradient': gradient_inputs
    }
    # print(response['attentions'][0][2])
    # print(jsonify(response))
    return jsonify(response)


@app.route('/AttentionParse', methods=['POST'])
def AttentionParse():
    data = request.get_json()
    attentions = np.array(data['attentions'])
    inputs_data = data['inputs']
    output_fields = data['output_fields']
    output_fields = [' ' + field for field in output_fields]
    output_indexes = np.array(data['output_indexes'])
    aggregationType = data['aggregation_type']
    selected_heads = np.array(data['selected_heads'])
    selected_layers = np.array(data['selected_layers'])
    heads_op = data['headsCustomOp']
    layers_op = data['layersCustomOp']
    input_text = inputs_data[0]['values'][0]['text']
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
    with open('data/table_1.json') as f:
        table_1 = json.load(f)
    with open('data/table_2.json') as f:
        table_2 = json.load(f)
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


@app.route('/generateTable', methods=['POST'])
def generateTable():
    data = request.get_json()
    output_fields = data['output_fields']
    dataset_type = str(data['exp_id'])
    pred.fields = [' ' + field for field in output_fields]
    pred.model_id = data['exp_id']
    with open('data/input_' + dataset_type + '.json') as f:
        input_list = json.load(f)
    input_list = [text + ' =' for text in input_list]
    table_json = pred.generateTable(input_list)
    with open('data/table_' + dataset_type + '.json', 'w') as outfile:
        json.dump(table_json, outfile)
    return 'Okay!'


if __name__ == '__main__':
    app.run()
