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
    input_text = f'{data[0]["field"]}: {data[0]["values"][0]["text"]} - {data[1]["field"]}: {data[1]["values"][0]["text"]} - {data[2]["field"]}: {data[2]["values"][0]["text"]} = '
    pred.fields = [' Cell Line', ' Cell Type', ' Tissue Type',' Factor']
    print(input_text)
    confidence = np.max(pred.predict([input_text]), 1)
    # print(f'the confidence is {confidence}')
    response_text = pred.generated_sequence
    # print(type(response_text))
    # print(response_text)
    first_split = response_text.split(' $ ')[0]
    first_split = first_split.split(' - ')
    second_split = [first_split[i].split(': ') for i in range(len(first_split))]
    second_split = second_split[1:]
    print(second_split)
    print(confidence)
    response = [dict(field=elem[0], value=elem[1], color=f'teal-{np.int(np.ceil(confidence[i]*5))}') for i, elem in enumerate(second_split)]
    # print(response)
    # print(jsonify(response))
    return jsonify(response)

@app.route('/prova', methods=['POST'])
def hola2():
    data = request.get_json()
    inp_data = data['inputs']
    input_text = f'{inp_data[0]["field"]}: {inp_data[0]["values"][0]["text"]} - {inp_data[1]["field"]}: {inp_data[1]["values"][0]["text"]} - {inp_data[2]["field"]}: {inp_data[2]["values"][0]["text"]} = '
    class_names = [pred.tokenizer.decode([x]) for x in range(len(pred.tokenizer))]
    explainer = LimeTextExplainer(class_names=class_names)
    pred.fields = [' ' + data['field']]
    # exp = explainer.explain_instance(input_text, pred.predict, num_features=4, top_labels=1,num_samples=10)
    # label = exp.available_labels()
    # print(f'The top class is {pred.tokenizer.decode(list(label))}')
    # weight_list = exp.as_list(label=label[0])
    weight_list = [('strain', 0.011063898017284577), ('musculus', 0.006857319100477079), ('H3K27me3', -0.005545956698784501)]
    result = [[], [], []]
    splits = [[inp_data[i]["values"][0]["text"]] for i in range(3)]
    # print(weight_list)
    max_scores = {'negative': 0, 'positive': 0}
    for (word, score) in weight_list:
        if score > 0:
            if score > max_scores['positive']:
                max_scores['positive'] = score
        else:
            if abs(score) > max_scores['negative']:
                max_scores['negative'] = abs(score)
        for i in range(3):
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
            if score_element != 0 :
                if score_element > 0:
                    sign = 'positive'
                    color = 'green'
                else:
                    sign = 'negative'
                    color = 'red'
                print(np.ceil(abs((score_element) / max_scores[sign])*5))
                opacity = int(np.ceil(abs((score_element) / max_scores[sign])*5)) if max_scores[sign] > 0 else int(np.ceil(score_element))
                result[i].append(dict(text=element, color=f'bg-{color}-{opacity}'))
            else:
                result[i].append(dict(text=element, color=f'bg-grey-3'))
    return jsonify(result)


if __name__ == '__main__':
    app.run()