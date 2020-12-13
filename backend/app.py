from flask import Flask, jsonify, request
from flask_cors import CORS
from model import Predictor
from forked_lime.lime.lime_text import LimeTextExplainer
import numpy as np

# configuration
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, support_credentials=True)
pred = Predictor()


@app.route('/prova2', methods=['POST'])
def hola():
    data = request.get_json()
    inputs_data = data['inputs']
    input_text = ' '
    for element in inputs_data:
        input_text += f'{element["field"]}: {element["values"][0]["text"]} - '
    input_text = input_text[:-2] + '='
    output_fields = data['output_fields']
    pred.fields = [' ' + field for field in output_fields]
    output_fields = [' ' + field for field in output_fields]
    pred.model_id = data['exp_id']
    print(input_text)
    pred.predict([input_text])
    confidences = pred.confidences
    output_ids = pred.generated_sequence_ids
    output_indexes = np.array(pred.indexes)
    input_ids = np.array(pred.tokenizer.encode(input_text))

    output_split = []
    for i in range(len(output_indexes)):
        if i < len(output_indexes) - 1:
            value = pred.tokenizer.decode(output_ids[
                output_indexes[i]:output_indexes[i+1]-len(
                    pred.tokenizer.encode(output_fields[i+1])
                )-2
            ])
            output_split.append([data['output_fields'][i], value])
        else:
            value = pred.tokenizer.decode(output_ids[output_indexes[i]:-2])
            output_split.append([data['output_fields'][i], value])

    outputs = [dict(
        field=elem[0],
        value=elem[1],
        color=f'teal-{10+np.int(np.ceil(confidences[i]*4))}' if (
            elem[1] != ' unknown' and elem[1] != ' None'
            ) else 'grey-3'
        ) for i, elem in enumerate(output_split)]
    response = {
        'outputs': outputs,
        'attentions': pred.attentions[
            :, :, len(input_ids):, :len(input_ids)
        ].tolist(),
        'output_indexes': output_indexes.tolist()
    }
    # print(response['attentions'][0][2])
    # print(jsonify(response))
    return jsonify(response)


@app.route('/prova3', methods=['POST'])
def hola3():
    data = request.get_json()
    attentions = np.array(data['attentions'])
    inputs_data = data['inputs']
    output_fields = data['output_fields']
    output_indexes = np.array(data['output_indexes'])
    aggregationType = data['aggregation_type']
    selected_heads = np.array(data['selected_heads'])
    selected_layers = np.array(data['selected_layers'])
    input_text = ' '
    print(selected_heads)
    print(selected_layers)
    print(selected_heads.shape)
    for element in inputs_data:
        input_text += f'{element["field"]}: {element["values"][0]["text"]} - '
    input_text = input_text[:-2] + '='
    print(attentions.shape)
    attentions_list = []
    if aggregationType == 'custom':
        if selected_heads.shape[0] == 0 or selected_layers.shape[0] == 0:
            attentions_custom = np.zeros([attentions.shape[-2],attentions.shape[-1]])
        else:
            attentions_custom = np.mean(
                np.mean(attentions[:, selected_heads], 1)[selected_layers], 0
            )
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

    input_fields = [' ' + element['field'] for element in inputs_data]
    values_indexes = []
    for field in input_fields:
        field_ids = np.array(pred.tokenizer.encode(field))
        input_ids = np.array(pred.tokenizer.encode(input_text))
        indexes = np.ones(
            len(np.where(
                input_ids == field_ids[0])[0])
        ) * -1
        for i, field_id in enumerate(field_ids):
            current_indexes = np.where(
                input_ids == field_id)[0]
            for n, index in enumerate(indexes):
                if i == 0:
                    indexes = current_indexes
                else:
                    for current_index in current_indexes:
                        if index + 1 == current_index:
                            indexes[n] = current_index
                            break
                        else:
                            indexes[n] = -1

        if (len(np.where(indexes != -1)[0]) == 0):
            index = -1
        else:
            index = indexes[np.where(indexes != 1)[0][0]] + 2

        values_indexes.append(index)

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
                    - 1, :
                ]
            else:
                scores = attentions[
                    output_indexes[j]:-1, :
                ]
            scores = np.mean(scores, axis=0)

            filtered_scores = []

            for i in range(len(values_indexes)):
                if i < len(values_indexes) - 1:
                    filtered_scores += list(scores[
                        values_indexes[i]:values_indexes[i+1]-len(
                            pred.tokenizer.encode(output_fields[i+1])
                        )-1
                    ])
                else:
                    filtered_scores += list(scores[values_indexes[i]:-1])
            max_scores = np.max(filtered_scores)
            max_scores = 1 if max_scores == 0.0 else max_scores
            scores = scores / max_scores

            input_list = list(zip(input_tokens, scores))

            attention_input = []

            for i in range(len(values_indexes)):
                if i < len(values_indexes) - 1:
                    attention_input.append(input_list[
                        values_indexes[i]:values_indexes[i+1]-len(
                            pred.tokenizer.encode(output_fields[i+1])
                        )-1
                    ])
                else:
                    attention_input.append(input_list[values_indexes[i]:-1])
            new_attention_input = []
            for values_list in attention_input:
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
                                (' ' or '-' or ':' or ';' or '(' or ')')):
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
                    opacity = np.int(np.ceil(value[1]*6))
                    bg_colors = f'bg-green-{opacity}' if (
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


@app.route('/prova', methods=['POST'])
def hola2():
    data = request.get_json()
    inp_data = data['inputs']
    input_text = ' '
    for element in inp_data:
        input_text += f'{element["field"]}: {element["values"][0]["text"]} - '
    input_text = input_text[:-2] + '='
    class_names = [pred.tokenizer.decode([x]) for x in range(len(pred.tokenizer))]
    explainer = LimeTextExplainer(class_names=class_names)
    pred.fields = [' ' + data['field']]
    pred.model_id = data['exp_id']
    exp = explainer.explain_instance(input_text, pred.predict, num_features=5, top_labels=1, num_samples=100)
    label = exp.available_labels()
    print(f'The top class is {pred.tokenizer.decode(list(label))}')
    weight_list = exp.as_list(label=label[0])
    # weight_list = [('strain', 0.011063898017284577), ('musculus', 0.006857319100477079), ('H3K27me3', -0.005545956698784501)]
    result = [[], [], []]
    splits = [[inp_data[i]["values"][0]["text"]] for i in range(len(inp_data))]
    # print(weight_list)
    max_scores = {'negative': 0, 'positive': 0}
    for (word, score) in weight_list:
        if score > 0:
            if score > max_scores['positive']:
                max_scores['positive'] = score
        else:
            if abs(score) > max_scores['negative']:
                max_scores['negative'] = abs(score)
        for i in range(len(inp_data)):
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
            score_element = weight_list[words.index(element)][1] if element in words else 0
            if score_element != 0:
                if score_element > 0:
                    sign = 'positive'
                    color = 'green'
                else:
                    sign = 'negative'
                    color = 'red'
                # print(np.ceil(abs((score_element) / max_scores[sign])*5))
                opacity = int(np.ceil(abs((score_element) / max_scores[sign])*5)) if max_scores[sign] > 0 else int(np.ceil(score_element))
                result[i].append(dict(text=element, color=f'bg-{color}-{opacity}'))
            else:
                result[i].append(dict(text=element, color='bg-white'))
    return jsonify(result)


if __name__ == '__main__':
    app.run()
