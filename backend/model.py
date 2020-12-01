import numpy as np
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch.nn.functional as F
from tqdm import tqdm


def create_tensors(data):
    tensor_list = []
    for elem in data:
        ids = torch.tensor(elem).unsqueeze(0)
        tensor_list.append(ids)
    return tensor_list


def tokenize_test_sequences(x, y, tokenizer, MAX_LEN=600):
    tokenized_x = []
    tokenized_y = []
    for _x, _y in zip(x, y):
        encoded_x = tokenizer.encode(_x)
        encoded_y = tokenizer.encode(_y)
        dim_x = len(encoded_x)
        dim_y = len(encoded_y)
        if(dim_x + dim_y <= MAX_LEN):
            tokenized_x.append(encoded_x)
            tokenized_y.append(encoded_y)
    excluded = len(x) - len(tokenized_x)
    print(f"{excluded} values were excluded because exceed a MAX \
        LENGTH of: {MAX_LEN}")
    return tokenized_x, tokenized_y


class Predictor:
    def __init__(self):
        self.fields = [' Cell Line', ' Cell Type', ' Tissue Type', ' Factor']
        self.device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu"
        )
        self.generated_sequence = None
        self.MAX_LEN = 400
        # Load pre-trained model (weights)
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

        # Load pre-trained model (weights)
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.tokenizer.add_special_tokens({'pad_token': '<pad>'})
        self.model.resize_token_embeddings(len(self.tokenizer))
        self.model.load_state_dict(
            torch.load(
                "Trained_Model.pth",
                map_location=torch.device(self.device)
            )
        )

        # Set the model in evaluation mode to deactivate the DropOut modules
        # This is IMPORTANT to have reproducible results during evaluation!
        self.model.eval()
        self.model.to(self.device)

    # this is used for lime and return the distributions of the output
    def predict(self, list_input_text):
        list_idx = []
        for i, input_text in enumerate(list_input_text):
            indexed_tokens = self.tokenizer.encode(
                input_text,
                truncation=True,
                max_length=self.MAX_LEN
            )
            tokens_tensor = torch.tensor([indexed_tokens])
            tokens_tensor = tokens_tensor.to(self.device)
            list_idx.append(tokens_tensor)
        results = []

        # Predict all tokens
        for input_idx in tqdm(list_idx, position=0, leave=True):
            input_idx = input_idx.view(1, 1, -1)
            # print(input_idx.size())
            with torch.no_grad():
                generated_sequence = []
                distributions = []
                predicted_token = 0

                while (predicted_token != self.tokenizer.encode("_") and
                       predicted_token != self.tokenizer.pad_token_id and
                       len(generated_sequence) < self.MAX_LEN):
                    out = self.model(input_idx)[0][0, 0]
                    last_tensor = out[-1]
                    predicted_token_tensor = torch.argmax(last_tensor)
                    distributions.append(F.softmax(last_tensor, 0))
                    predicted_token = predicted_token_tensor.item()
                    input_idx = torch.cat(
                        (input_idx, predicted_token_tensor.view(1, 1, 1)),
                        dim=-1
                    )
                    generated_sequence.append(predicted_token)

                print(self.tokenizer.decode(generated_sequence))
                for field in self.fields:
                    field_tokens = np.array(self.tokenizer.encode(field))
                    generated_sequence = np.array(generated_sequence)
                    indexes = np.ones(
                        len(np.where(
                            generated_sequence == field_tokens[0])[0])
                    ) * -1
                    for i, token in enumerate(field_tokens):
                        current_indexes = np.where(
                            generated_sequence == token)[0]
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
                        index = indexes[np.where(indexes != -1)[0][0]] + 2
                    # print(f'final index is {index}')
                    # print(
                    #     self.tokenizer.decode(
                    #         [generated_sequence[index - 2]]
                    #     )
                    # )
                    # print(self.tokenizer.decode([generated_sequence[index]]))
                    results.append(distributions[index].detach().cpu().numpy())
        results_array = np.array(results)
        self.generated_sequence = self.tokenizer.decode(generated_sequence)
        return results_array

    # the this is used to return the generated string
    # def inference(self, input):
    #     test_inp = []
    #     test_out = []
    #     test_inp.append(input)
    #     test_out.append("Don't care")
    #     test_tokens_X, test_tokens_y = tokenize_test_sequences(
    #         test_inp,
    #         test_out,
    #         self.tokenizer,
    #         self.MAX_LEN
    #     )
    #     X_tensors, Y_tensors = create_tensors(test_tokens_X), \
    #         create_tensors(test_tokens_y)
    #     test_data = []
    #     for x, y in zip(X_tensors, Y_tensors):
    #         tmp = [x, y]
    #         test_data.append(tmp)

    #     testloader = torch.utils.data.DataLoader(
    #         test_data,
    #         batch_size=1,
    #         shuffle=False
    #     )

    #     with torch.no_grad():
    #         for it, elem in enumerate(tqdm(testloader)):
    #             inputs = elem[0]
    #             # labels = elem[1]
    #             # target_sequence = labels[0,0].tolist()
    #             inputs = inputs.to(self.device)
    #             predicted_token = 0
    #             generated_sequence = []
    #             while(predicted_token != self.tokenizer.encode("_") and
    #                   predicted_token != self.tokenizer.pad_token_id and
    #                   len(generated_sequence) < self.MAX_LEN):
    #                 out = self.model(inputs)[0][0, 0]
    #                 last_tensor = out[-1]
    #                 predicted_token_tensor = torch.argmax(last_tensor)
    #                 predicted_token = predicted_token_tensor.item()
    #                 inputs = torch.cat(
    #                     (inputs, predicted_token_tensor.view(1, 1, 1)),
    #                     dim=-1
    #                 )
    #                 generated_sequence.append(predicted_token)
    #             # print('la roba è questa: ')
    #             # print(self.tokenizer.decode(generated_sequence))
    #             return self.tokenizer.decode(generated_sequence)
