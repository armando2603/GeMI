from collections import OrderedDict
import numpy as np
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, GPT2Config
import torch.nn.functional as F
from tqdm import tqdm
from os import path


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
        self.MAX_LEN = 350
        self.model = None
        self.model_id = None
        # Load pre-trained model (weights)
        model_name = 'gpt2'
        self.config = GPT2Config()
        self.model = GPT2LMHeadModel(self.config)
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.tokenizer.add_special_tokens({
            'pad_token': '<PAD>',
            'bos_token': '<BOS>',
            'eos_token': '<EOS>',
            'sep_token': '<SEP>',
            'additional_special_tokens': ['<SEPO>']
        })
        self.base_model = GPT2LMHeadModel(self.config)
        self.base_model.resize_token_embeddings(len(self.tokenizer))
        self.base_model.eval()
        # self.model_1.resize_token_embeddings(len(self.tokenizer))
        # self.model_2.resize_token_embeddings(len(self.tokenizer))

        self.model.resize_token_embeddings(len(self.tokenizer))
        self.name_model_2 = 'checkpoint_2_lessout-epoch=25-val_loss=0.253.ckpt'
        self.name_model_1 = 'checkpoint_1-epoch=13-val_loss=0.063.ckpt'

        # checkpoint = torch.load('Models/' + self.name_model_2)
        # if 'state_dict' in checkpoint.keys():
        #     state_dict = checkpoint['state_dict']
        #     new_state_dict = OrderedDict()
        #     for k, v in state_dict.items():
        #         if k[:6] == 'model.':
        #             name = k[6:]
        #         else:
        #             name = k
        #         new_state_dict[name] = v
        #     self.model.load_state_dict(new_state_dict)
        #     torch.save(self.model.state_dict(), 'Models/' + self.name_model_2)

        # checkpoint = torch.load('Models/' + self.name_model_1)
        # if 'state_dict' in checkpoint.keys():
        #     state_dict = checkpoint['state_dict']
        #     new_state_dict = OrderedDict()
        #     for k, v in state_dict.items():
        #         if k[:6] == 'model.':
        #             name = k[6:]
        #         else:
        #             name = k
        #         new_state_dict[name] = v
        #     self.model.load_state_dict(new_state_dict)
        #     torch.save(self.model.state_dict(), 'Models/' + self.name_model_1)

        # self.model.load_state_dict(
        #     torch.load('Models/' + self.name_model_2)
        # )
        # model 2
        # self.model.load_state_dict(
        #     torch.load('Models/checkpoint_2_nomask_new-epoch=32-val_loss=0.212.ckpt')
        # )

        # self.model.eval()
        # self.model.to(self.device)

        # self.model_1.eval()
        # self.model_1.to(self.device)
        # self.model_2.eval()

        # self.model_2.to(self.device)

    def predict(self, list_input_text):
        self.model = self.base_model.to(self.device)
        if self.model_id == 2:
            if path.isfile('Models/' + 'augmented_' + self.name_model_2):
                augmented = 'augmented_'
            else:
                augmented = ''
            self.model.load_state_dict(
                torch.load('Models/' + augmented + self.name_model_2)
            )
        if self.model_id == 1:
            if path.isfile('Models/' + 'augmented_' + self.name_model_1):
                augmented = 'augmented_'
            else:
                augmented = ''
            self.model.load_state_dict(
                torch.load('Models/' + augmented + self.name_model_1)
            )
        list_idx = []
        for i, input_text in enumerate(list_input_text):
            end_id = self.tokenizer.eos_token_id
            print(input_text)
            indexed_tokens = self.tokenizer.encode(
                input_text,
                truncation=True,
                max_length=self.MAX_LEN + 3
            )
            # print(self.tokenizer.decode(indexed_tokens))
            tokens_tensor = torch.tensor([indexed_tokens])
            tokens_tensor = tokens_tensor
            list_idx.append(tokens_tensor)
        results = []
        grad_explain = []
        # Predict all tokens
        for input_ids in tqdm(list_idx, position=0, leave=True):
            # print(input_ids.size())

            input_ids = torch.cat(
                (
                    torch.tensor([[self.tokenizer.bos_token_id]]),
                    input_ids,
                    torch.tensor([[self.tokenizer.sep_token_id]])
                ),
                dim=-1
            ).to(self.device)
            input_length = input_ids.shape[1]
            generated_sequence = []
            distributions = []
            # colon_id = self.tokenizer.encode(':')[0]
            # SEPO_id = self.tokenizer.encode('<SEPO>')[0]
            # attn_mask_value = torch.zeros(1, 0, device=self.device)
            # is_value = False
            # attn_mask = torch.ones(input_ids.shape, device=self.device)
            while(len(generated_sequence) < 300):

                inputs_embeds, token_ids_tensor_one_hot = \
                    self._get_embeddings(input_ids[0])
                inputs = inputs_embeds.unsqueeze(0)
                # outputs = self.model(inputs_embeds=inputs, attention_mask=attn_mask)
                outputs = self.model(
                    inputs_embeds=inputs,
                    output_attentions=True,
                    return_dict=True
                )
                next_token_logits = outputs.logits[:, -1, :]
                predicted_token_tensor = torch.argmax(next_token_logits)
                # if predicted_token_tensor == SEPO_id:
                #     is_value = False
                #     attn_mask[0, -attn_mask_value.shape[1]:] = attn_mask_value
                #     attn_mask_value = torch.zeros(1, 0, device=self.device)
                # attn_mask = torch.cat((attn_mask, torch.ones(1, 1, device=self.device)), dim=-1)
                # if is_value:
                #     attn_mask_value = torch.cat((attn_mask_value, torch.zeros(1, 1, device=self.device)), dim=-1)
                # if predicted_token_tensor == colon_id:
                #     is_value = True
                
                # print(self.tokenizer.decode(generated_sequence))
            # while(predicted_token != self.tokenizer.pad_token_id
            #         and predicted_token != end_id
            #         and len(generated_sequence) < 300):

            #     inputs_embeds, token_ids_tensor_one_hot = \
            #         self._get_embeddings(input_ids[0])
            #     inputs = inputs_embeds.unsqueeze(0)
            #     outputs = self.model(inputs_embeds=inputs)

            #     next_token_logits = outputs.logits[:, -1, :]
            #     predicted_token_tensor = torch.argmax(next_token_logits)

                distributions.append(
                    F.softmax(next_token_logits[0], 0).detach()
                )
                prediction_logit = outputs.logits[
                    0,
                    -1,
                    predicted_token_tensor
                ]
                grad_x_input = gradient_x_inputs_attribution(
                    prediction_logit,
                    inputs_embeds
                )
                grad_explain.append(
                    grad_x_input[:input_length].detach()
                )
                input_ids = torch.cat(
                    (input_ids, predicted_token_tensor.view(1, 1)),
                    dim=-1
                ).detach()
                generated_sequence.append(predicted_token_tensor.detach())
                if predicted_token_tensor == end_id:
                    break
            self.attentions = [
                layer[0].detach().cpu().numpy()
                for layer in outputs.attentions
            ]
            grad_explain = [
                explain.cpu().numpy() for explain in grad_explain
            ]
            distributions = [
                distribution.cpu().numpy() for distribution in distributions
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
                results.append(distributions[index])

            self.confidences = []
            for j in range(len(self.indexes)):
                if self.indexes[j] == -1:
                    self.confidences.append(1)
                else:
                    # confidence 1st token
                    out_prob = distributions[self.indexes[j]]
                    self.confidences.append(np.max(out_prob))

                    # confidence as mul of confidences
                    # if j < len(indexes) - 1:
                    #     out_prob = distributions[
                    #         self.indexes[j]:self.indexes[j+1]
                    #         - len(
                    #             self.tokenizer.encode(self.fields[j+1])
                    #         ) - 2
                    #     ]
                    #     self.confidences.append(np.multiply.reduce(
                    #         np.max(out_prob, 1),
                    #         0
                    #     ))
                    # else:
                    #     out_prob = distributions[self.indexes[j]:-1]
                    #     self.confidences.append(np.multiply.reduce(
                    #         np.max(out_prob, 1),
                    #         0
                    #     ))

        results_array = np.array(results)
        self.generated_sequence_ids = generated_sequence
        # self.model = self.model.to('cpu')
        # self.model = self.base_model
        if self.model_id == 1:
            del self.model
            torch.cuda.empty_cache()
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

    def generateTable(self, list_input_dict):
        self.model = self.base_model.to(self.device)
        table_json = []
        model_ids = [2, 1]
        fields_2 = self.fields
        with torch.no_grad():
            for it, input_dict in enumerate(tqdm(list_input_dict)):
                prediction_list = []
                fields_dict = dict()
                for model_id in model_ids:
                    if model_id == 2:
                        if path.isfile('Models/' + 'augmented_' + self.name_model_2):
                            augmented = 'augmented_'
                        else:
                            augmented = ''
                        self.model.load_state_dict(
                            torch.load('Models/' + augmented + self.name_model_2)
                        )
                        self.fields = fields_2
                    if model_id == 1:
                        if path.isfile('Models/' + 'augmented_' + self.name_model_1):
                            augmented = 'augmented_'
                        else:
                            augmented = ''
                        self.model.load_state_dict(
                            torch.load('Models/' + augmented + self.name_model_1)
                        )
                        self.fields = ['Cell Line', 'Tissue Type']
                    # print(input_dict['input_text'])
                    input_ids = self.tokenizer.encode(
                        input_dict['input_text'].strip(),
                        return_tensors='pt',
                        truncation=True,
                        max_length=self.MAX_LEN
                    )
                    # print(input_ids.shape)
                    input_ids = torch.cat(
                        (
                            torch.tensor([[self.tokenizer.bos_token_id]]),
                            input_ids,
                            torch.tensor([[self.tokenizer.sep_token_id]])
                        ),
                        dim=-1
                    )
                    input_ids = input_ids.to(self.device)
                    end_id = self.tokenizer.eos_token_id
                    generated_sequence = []
                    distributions = []
                    # colon_id = self.tokenizer.encode(':')[0]
                    # SEPO_id = self.tokenizer.encode('<SEPO>')[0]
                    # attn_mask_value = torch.zeros(1, 0, device=self.device)
                    # is_value = False
                    # attn_mask = torch.ones(input_ids.shape, device=self.device)
                    past = None
                    while(len(generated_sequence) < 300):
                        out = self.model(
                            input_ids,
                            # attention_mask=attn_mask,
                            past_key_values=past,
                            use_cache=True,
                            return_dict=True
                        )
                        past = out.past_key_values
                        last_tensor = out.logits[0, -1, :]
                        distributions.append(
                            F.softmax(last_tensor, 0)
                        )
                        predicted_token_tensor = torch.argmax(last_tensor)
                        # if predicted_token_tensor == SEPO_id:
                        #     is_value = False
                        #     attn_mask[0, -attn_mask_value.shape[1]:] = attn_mask_value
                        #     attn_mask_value = torch.zeros(1, 0, device=self.device)
                        # attn_mask = torch.cat((attn_mask, torch.ones(1, 1, device=self.device)), dim=-1)
                        # if is_value:
                        #     attn_mask_value = torch.cat((attn_mask_value, torch.zeros(1, 1, device=self.device)), dim=-1)
                        # if predicted_token_tensor == colon_id:
                        #     is_value = True
                        input_ids = predicted_token_tensor.view(1, 1)
                        # input_ids = torch.cat(
                        #     (input_ids, predicted_token_tensor.view(1, 1)), dim=-1)
                        generated_sequence.append(predicted_token_tensor)
                        if predicted_token_tensor == end_id:
                            break
                    # print(self.tokenizer.decode(generated_sequence))
                    prediction_list.append(generated_sequence)
                    distributions = [distribution.cpu().numpy() for distribution in distributions]
                    values, confidences = self.extract_values(
                        generated_sequence, distributions
                    )
                    for i, field in enumerate(self.fields):
                        fields_dict[field] = dict(
                            value=values[i].strip(),
                            confidence=np.round(np.float(confidences[i]), 2),
                            fixed=False
                        )
                prediction = (
                    prediction_list[0][:-1]
                    + [int(self.tokenizer.eos_token_id)]
                    + prediction_list[1]
                )
                # print(self.tokenizer.decode(prediction))
                table_json.append(
                    dict(
                        id=it,
                        GSE=input_dict['GSE'],
                        GSM=input_dict['GSM'],
                        input=self.tokenizer.decode(
                            self.tokenizer.encode(
                                input_dict['input_text'].strip(),
                                truncation=True,
                                max_length=self.MAX_LEN
                            )
                        ),
                        prediction_text=self.tokenizer.decode(prediction),
                        fields=fields_dict
                    )
                )
            del self.model
            torch.cuda.empty_cache()
            return table_json

    def extract_values(self, text_ids, distributions):
        output_indexes = []
        for field in self.fields:
            field_tokens = np.array(self.tokenizer.encode(field))
            generated_sequence = np.array(text_ids)
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
            output_indexes.append(index)

        assert not all(elem == -1 for elem in output_indexes),\
            f'One sample are not recognized: {self.tokenizer.decode(generated_sequence)}'
        values = []
        for i in range(len(output_indexes)):
            if output_indexes[i] == -1:
                values.append('<missing>')
            else:
                if i < len(output_indexes) - 1:
                    values.append(self.tokenizer.decode(generated_sequence[
                        output_indexes[i]:output_indexes[i+1]-len(
                            self.tokenizer.encode(self.fields[i+1])
                        )-2
                    ]))
                else:
                    values.append(
                        self.tokenizer.decode(
                            generated_sequence[output_indexes[i]:-1]
                            )
                    )

        confidences = []
        for j in range(len(output_indexes)):
            if output_indexes[j] == -1:
                confidences.append(np.float64(1))
            else:
                # confidence 1st token
                out_prob = distributions[output_indexes[j]]
                confidences.append(np.max(out_prob))
                # confidence as mul of confidences
                # if j < len(indexes) - 1:
                #     out_prob = distributions[
                #         output_indexes[j]:output_indexes[j+1]
                #         - len(
                #             self.tokenizer.encode(self.fields[j+1])
                #         ) - 2
                #     ]
                #     confidences.append(np.multiply.reduce(
                #         np.max(out_prob, 1),
                #         0
                #     ))
                # else:
                #     out_prob = distributions[output_indexes[j]:-1]
                #     confidences.append(np.multiply.reduce(
                #         np.max(out_prob, 1),
                #         0
                #     ))

        return values, confidences

    def onlineLearning(self, input_text, output_text):
        self.model = self.base_model.to(self.device)
        if self.model_id == 2:
            if path.isfile('Models/' + 'augmented_' + self.name_model_2):
                augmented = 'augmented_'
            else:
                augmented = ''
            self.model.load_state_dict(
                torch.load('Models/' + augmented + self.name_model_2)
            )
        if self.model_id == 1:
            if path.isfile('Models/' + 'augmented_' + self.name_model_1):
                augmented = 'augmented_'
            else:
                augmented = ''
            self.model.load_state_dict(
                torch.load('Models/' + augmented + self.name_model_1)
            )
        input_ids = self.tokenizer.encode(
            input_text,
            return_tensors='pt',
            truncation=True,
            max_length=self.MAX_LEN
        ).to(self.device)
        print(output_text)
        output_ids = self.tokenizer.encode(
            output_text,
            return_tensors='pt'
        ).to(self.device)
        inp_out_ids = torch.cat(
            (
                torch.tensor([[self.tokenizer.bos_token_id]], device=self.device),
                input_ids,
                torch.tensor([[self.tokenizer.sep_token_id]], device=self.device),
                output_ids
            ),
            dim=-1
        )
        inp_out_ids = inp_out_ids
        labels = inp_out_ids.clone().detach()
        labels[0, :-output_ids.shape[1]] = torch.ones(
            input_ids.shape[1] + 2
        ) * -100

        optimizer = torch.optim.Adam(self.model.parameters(), lr=5e-5)
        new_output = torch.empty(output_ids.shape, device=self.device)
        not_match = True
        max_epochs = 3
        epoch = 0
        while (not_match and epoch < max_epochs):
            epoch += 1
            self.model.train()
            optimizer.zero_grad()
            output = self.model(inp_out_ids, labels=labels, return_dict=True)
            loss = output.loss
            print(loss)
            loss.backward()
            optimizer.step()
            self.model.eval()
            with torch.no_grad():
                past = None
                inp = torch.cat(
                    (
                        torch.tensor(
                            [[self.tokenizer.bos_token_id]],
                            device=self.device
                        ),
                        input_ids,
                        torch.tensor(
                            [[self.tokenizer.sep_token_id]],
                            device=self.device
                        )
                    ),
                    dim=-1
                )
                generated_sequence = torch.zeros(
                    (1, 0),
                    device=self.device
                ).long()
                while(len(generated_sequence) < 300):
                    out = self.model(
                        inp,
                        # attention_mask=attn_mask,
                        past_key_values=past,
                        use_cache=True,
                        return_dict=True
                    )
                    past = out.past_key_values
                    last_tensor = out.logits[0, -1, :]
                    predicted_token_tensor = torch.argmax(last_tensor)
                    inp = predicted_token_tensor.view(1, 1)
                    generated_sequence = torch.cat(
                        (generated_sequence, predicted_token_tensor.view(1,1)),
                        dim=-1
                    )
                    if predicted_token_tensor == self.tokenizer.eos_token_id:
                        break
                new_output = generated_sequence
                if new_output.shape == output_ids.shape:
                    if torch.all(new_output.eq(output_ids)):
                        not_match = False
        if self.model_id == 2:
            torch.save(
                self.model.state_dict(),
                'Models/augmented_checkpoint_2_lessout-epoch=25-val_loss=0.253.ckpt'
            )
            del self.model
            torch.cuda.empty_cache()
        if self.model_id == 1:
            torch.save(
                self.model.state_dict(),
                'Models/augmented_checkpoint_1-epoch=13-val_loss=0.063.ckpt'
            )
        # torch.save(
        #     self.model.state_dict(),
        #     'Models/' + self.name_model_2
        # )
        # self.model.load_state_dict(
        #     torch.load('Models/' + self.name_model_2)
        # )
        # self.model.eval()
