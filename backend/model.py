import numpy as np
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch.nn.functional as F
from tqdm import tqdm


class Predictor:
    def __init__(self):
        self.fields = [' Cell Line', ' Cell Type', ' Tissue Type', ' Factor']
        self.device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu"
        )
        self.generated_sequence = None
        self.MAX_LEN = 400
        # Load pre-trained model (weights)
        model_name = 'gpt2'
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)

        # Load pre-trained model (weights)
        self.model = GPT2LMHeadModel.from_pretrained(
            model_name,
            output_attentions=True,
            return_dict=True
        )
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
        tokenof_ = self.tokenizer.encode("_")
        # Predict all tokens
        for input_idx in tqdm(list_idx, position=0, leave=True):
            input_idx = input_idx.view(1, -1)
            # print(input_idx.size())
            with torch.no_grad():
                generated_sequence = []
                distributions = []
                predicted_token = 0

                while (predicted_token != tokenof_ and
                       predicted_token != self.tokenizer.pad_token_id and
                       len(generated_sequence) < 50):
                    outputs = self.model(input_idx)
                    next_token_logits = outputs.logits[:, -1, :]
                    predicted_token_tensor = torch.argmax(next_token_logits)
                    distributions.append(F.softmax(next_token_logits[0], 0))
                    predicted_token = predicted_token_tensor.item()
                    input_idx = torch.cat(
                        (input_idx, predicted_token_tensor.view(1, 1)),
                        dim=-1
                    )
                    generated_sequence.append(predicted_token)
                self.attentions = [
                    layer[0].detach().cpu().numpy()
                    for layer in outputs.attentions
                ]
                self.attentions = np.array(self.attentions)
                self.attentions = np.mean(self.attentions, 1)
                self.attentions = np.mean(self.attentions, 0)
                print(self.tokenizer.decode(generated_sequence))

                self.indexes = []
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
                    # print(self.tokenizer.decode([generated_sequence[index-2]]))
                    # print(self.tokenizer.decode([generated_sequence[index]]))
                    if index >= len(generated_sequence):
                        index = -1
                    self.indexes.append(index)
                    print(index)
                    print(len(distributions))
                    results.append(distributions[index].detach().cpu().numpy())
        results_array = np.array(results)
        self.generated_sequence = self.tokenizer.decode(generated_sequence)
        return results_array
