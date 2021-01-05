import numpy as np
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch.nn.functional as F
from tqdm import tqdm


def gradient_x_inputs_attribution(prediction_logit, inputs_embeds):

    inputs_embeds.retain_grad()
    # back-prop gradient
    prediction_logit.backward(retain_graph=True)
    grad = inputs_embeds.grad
    # This should be equivalent to
    # grad = torch.autograd.grad(prediction_logit, inputs_embeds)[0]

    # Grad X Input
    grad_x_input = grad * inputs_embeds

    # Turn into a scalar value for each input token by taking L2 norm
    feature_importance = torch.norm(grad_x_input, dim=1)

    # Normalize so we can show scores as percentages
    token_importance_normalized = feature_importance / torch.sum(
        feature_importance)

    # Zero the gradient for the tensor so next backward() calls don't have
    # gradients accumulating
    inputs_embeds.grad.data.zero_()
    return token_importance_normalized


class Predictor:
    def __init__(self):
        self.pretrained_model = ''
        self.fields = []
        self.device = torch.device(
            "cuda:0" if torch.cuda.is_available() else "cpu"
        )
        self.generated_sequence = None
        self.MAX_LEN = 400
        self.model = None
        self.model_id = None
        # Load pre-trained model (weights)
        model_name = 'distilgpt2'
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)

        # Load pre-trained model (weights)
        self.model_1 = GPT2LMHeadModel.from_pretrained(
            'gpt2',
            output_attentions=True,
            return_dict=True
        )
        self.model_2 = GPT2LMHeadModel.from_pretrained(
            model_name,
            output_attentions=True,
            return_dict=True
        )
        self.tokenizer.add_special_tokens({'pad_token': '<pad>'})
        self.model_1.resize_token_embeddings(len(self.tokenizer))
        self.model_1.load_state_dict(
            torch.load(
                'Trained_Model.pth',
                map_location=torch.device(self.device)
            )
        )
        self.model_2.resize_token_embeddings(len(self.tokenizer))
        self.model_2.load_state_dict(
            torch.load(
                'Trained_Model_2.pth',
                map_location=torch.device(self.device)
            )
        )

        # Set the model in evaluation mode to deactivate the DropOut modules
        # This is IMPORTANT to have reproducible results during evaluation!
        self.model_1.eval()
        self.model_1.to(self.device)

        self.model_2.eval()
        self.model_2.to(self.device)

    # this is used for lime and return the distributions of the output
    def predict(self, list_input_text):
        assert self.model_id is not None, 'Please set self.model_id to 1 or 2'
        if self.model_id == 1:
            self.model = self.model_1
        if self.model_id == 2:
            self.model = self.model_2
        list_idx = []
        for i, input_text in enumerate(list_input_text):
            if input_text[-1] != '=' and input_text[-1] != ' ':
                input_text += ' ='
            indexed_tokens = self.tokenizer.encode(
                input_text,
                truncation=True,
                max_length=self.MAX_LEN
            )
            tokens_tensor = torch.tensor([indexed_tokens])
            tokens_tensor = tokens_tensor.to(self.device)
            list_idx.append(tokens_tensor)
        results = []
        grad_explain = []
        tokenof_ = self.tokenizer.encode("_")
        # Predict all tokens
        for input_ids in tqdm(list_idx, position=0, leave=True):
            input_ids = input_ids.view(1, -1)
            input_length = input_ids.shape[1]
            # print(input_ids.size())

            generated_sequence = []
            distributions = []
            predicted_token = 0

            while (predicted_token != tokenof_ and
                    predicted_token != self.tokenizer.pad_token_id and
                    len(generated_sequence) < 260):

                inputs_embeds, token_ids_tensor_one_hot = \
                    self._get_embeddings(input_ids[0])
                inputs = inputs_embeds.unsqueeze(0)
                outputs = self.model(inputs_embeds=inputs)

                next_token_logits = outputs.logits[:, -1, :]
                predicted_token_tensor = torch.argmax(next_token_logits)
                distributions.append(F.softmax(next_token_logits[0], 0))
                predicted_token = predicted_token_tensor.item()
                prediction_logit = outputs.logits[
                    0,
                    -1,
                    predicted_token
                ]
                grad_x_input = gradient_x_inputs_attribution(
                    prediction_logit,
                    inputs_embeds
                )
                grad_explain.append(
                    grad_x_input[:input_length - 1].detach().cpu().numpy()
                )
                input_ids = torch.cat(
                    (input_ids, predicted_token_tensor.view(1, 1)),
                    dim=-1
                )
                generated_sequence.append(predicted_token)
            self.attentions = [
                layer[0].detach().cpu().numpy()
                for layer in outputs.attentions
            ]
            self.grad_explain = np.array(grad_explain)
            self.attentions = np.array(self.attentions)
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
                if index >= len(generated_sequence):
                    index = -1
                self.indexes.append(index)
                # print(f'final index is {index}')
                # print(self.tokenizer.decode([generated_sequence[index-2]]))
                # print(self.tokenizer.decode([generated_sequence[index]]))
                # print(index)
                # print(len(distributions))
                results.append(distributions[index].detach().cpu().numpy())

            self.confidences = []
            for j in range(len(self.indexes)):
                if j < len(self.indexes) - 1:
                    outputs_prob = distributions[
                        self.indexes[j]:
                        + self.indexes[j+1]
                        - len(self.tokenizer.encode(self.fields[j+1]))
                        - 1
                    ]
                else:
                    outputs_prob = distributions[
                        self.indexes[j]:-1
                    ]
                outputs_prob = [
                    out_prob.detach().cpu().numpy() for
                    out_prob in outputs_prob
                ]
                outputs_conf = np.max(outputs_prob, axis=1)
                self.confidences.append(np.mean(outputs_conf, axis=0))

        results_array = np.array(results)
        self.generated_sequence_ids = generated_sequence
        return results_array

    def _get_embeddings(self, input_ids):
        """
        Takes the token ids of a sequence, returnsa matrix of their embeddings.
        """
        embedding_matrix = self.model.transformer.wte.weight

        vocab_size = embedding_matrix.shape[0]

        one_hot_tensor = torch.zeros(
            len(input_ids), vocab_size
        ).to(self.device).scatter_(1, input_ids.unsqueeze(1), 1.)

        token_ids_tensor_one_hot = one_hot_tensor.clone().requires_grad_(True)
        # token_ids_tensor_one_hot.requires_grad_(True)

        inputs_embeds = torch.matmul(token_ids_tensor_one_hot, embedding_matrix)
        return inputs_embeds, token_ids_tensor_one_hot
