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
        print(torch.cuda.is_available())
        self.generated_sequence = None
        self.MAX_LEN = 350
        self.model = None
        self.status = 0
        self.model_id = None
        # Load pre-trained model (weights)
        model_name = 'gpt2'
        self.config = GPT2Config()
        self.model = GPT2LMHeadModel(self.config)
        self.model.eval()
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.tokenizer.add_special_tokens({
            'pad_token': '<PAD>',
            'bos_token': '<BOS>',
            'eos_token': '<EOS>',
            'sep_token': '<SEP>'
        })
        self.base_model = GPT2LMHeadModel(self.config)
        self.base_model.resize_token_embeddings(len(self.tokenizer))
        self.base_model.eval()
        # self.model_1.resize_token_embeddings(len(self.tokenizer))
        # self.model_2.resize_token_embeddings(len(self.tokenizer))

        self.model.resize_token_embeddings(len(self.tokenizer))
        # self.name_model = 'checkpoint_4-epoch=14-val_loss=0.306.ckpt'
        self.name_model = 'checkpoint-4-8+-epoch=12-val_loss=0.287.ckpt'
        checkpoint = torch.load('Models/' + self.name_model, map_location='cpu')
        if 'state_dict' in checkpoint.keys():
            state_dict = checkpoint['state_dict']
            new_state_dict = OrderedDict()
            for k, v in state_dict.items():
                if k[:6] == 'model.':
                    name = k[6:]
                else:
                    name = k
                new_state_dict[name] = v
            self.model.load_state_dict(new_state_dict)
            torch.save(self.model.state_dict(), 'Models/' + self.name_model)
        else:
            del checkpoint

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

    def predict(self, list_input_text, fields):
        self.fields = fields
        self.model = self.base_model.to(self.device)
        if path.isfile('Models/' + 'augmented_' + self.name_model):
            augmented = 'augmented_'
        else:
            augmented = ''
        self.model.load_state_dict(
            torch.load(
                'Models/' + augmented + self.name_model, map_location=self.device
            )
        )
        # Predict all tokens
        for input_text in tqdm(list_input_text, position=0, leave=True):
            # print(input_ids.size())
            self.confidences = []
            self.grad_explains = []
            self.generated_sequences = []
            end_id = self.tokenizer.eos_token_id
            print(input_text)
            prefix_input_ids = self.tokenizer.encode(
                input_text,
                return_tensors='pt',
                truncation=True,
                max_length=self.MAX_LEN + 3
            )
            for field in self.fields:
                grad_explain = []
                conditional_ids = self.tokenizer.encode(
                    field + ':',
                    return_tensors='pt',
                    truncation=True,
                    max_length=self.MAX_LEN
                )
                input_ids = torch.cat(
                    (
                        torch.tensor([[self.tokenizer.bos_token_id]]),
                        prefix_input_ids,
                        torch.tensor([[self.tokenizer.sep_token_id]]),
                        conditional_ids
                    ),
                    dim=-1
                ).to(self.device)
                # print(self.tokenizer.decode(input_ids[0]))
                input_length = prefix_input_ids.shape[1]
                generated_sequence = []
                distributions = []
                # colon_id = self.tokenizer.encode(':')[0]
                # SEPO_id = self.tokenizer.encode('<SEPO>')[0]
                # attn_mask_value = torch.zeros(1, 0, device=self.device)
                # is_value = False
                # attn_mask = torch.ones(input_ids.shape, device=self.device)
                while(len(generated_sequence) < 30):

                    inputs_embeds, token_ids_tensor_one_hot = \
                        self._get_embeddings(input_ids[0])
                    inputs = inputs_embeds.unsqueeze(0)
                    outputs = self.model(
                        inputs_embeds=inputs,
                        return_dict=True
                    )
                    next_token_logits = outputs.logits[:, -1, :]
                    predicted_token_tensor = torch.argmax(next_token_logits)

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
                        grad_x_input[1:(input_length + 1)].detach()
                    )
                    input_ids = torch.cat(
                        (input_ids, predicted_token_tensor.view(1, 1)),
                        dim=-1
                    ).detach()
                    generated_sequence.append(predicted_token_tensor.detach())
                    if predicted_token_tensor == end_id:
                        break

                grad_explain = [
                    explain.cpu().numpy() for explain in grad_explain
                ]
                distributions = [
                    distribution.cpu().numpy() for distribution in distributions
                    ]
                self.grad_explains.append(np.array(grad_explain))
                print(self.tokenizer.decode(generated_sequence))

                output_index = 0

                # confidence 1st token
                out_prob = distributions[output_index]
                self.confidences.append(np.max(out_prob))

                # confidence as mul of confidences
                #     out_prob = distributions[self.indexes[j]:-1]
                #     self.confidences.append(np.multiply.reduce(
                #         np.max(out_prob, 1),
                #         0
                #     ))

                self.generated_sequences.append(generated_sequence)
        # self.model = self.model.to('cpu')
        # self.model = self.base_model
        if self.model_id == 1:
            del self.model
            with torch.cuda.device(self.device):
                torch.cuda.empty_cache()
        return self.generated_sequences, self.confidences, self.grad_explains

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

    def generateTable(self, list_input_dict, fields):
        self.status = 0
        self.model = self.base_model.to(self.device)
        table_json = []
        self.fields = fields
        if path.isfile('Models/' + 'augmented_' + self.name_model):
            augmented = 'augmented_'
        else:
            augmented = ''
        self.model.load_state_dict(
            torch.load(
                'Models/' + augmented + self.name_model, map_location=self.device
            )
        )
        with torch.no_grad():
            for it, input_dict in enumerate(tqdm(list_input_dict)):
                self.status = round((it + 1)/len(list_input_dict), 2) * 100
                prediction_list = []
                fields_dict = dict()
                pre_input_ids = self.tokenizer.encode(
                    input_dict['input_text'].lower(),
                    return_tensors='pt',
                    truncation=True,
                    max_length=self.MAX_LEN
                )
                for field in self.fields:
                    # print(input_dict['input_text'])
                    conditional_ids = self.tokenizer.encode(
                        field + ':',
                        return_tensors='pt',
                        truncation=True,
                        max_length=self.MAX_LEN
                    )
                    # print(input_ids.shape)
                    input_ids = torch.cat(
                        (
                            torch.tensor([[self.tokenizer.bos_token_id]]),
                            pre_input_ids,
                            torch.tensor([[self.tokenizer.sep_token_id]]),
                            conditional_ids
                        ),
                        dim=-1
                    ).to(self.device)
                    end_id = self.tokenizer.eos_token_id
                    generated_sequence = []
                    distributions = []
                    # colon_id = self.tokenizer.encode(':')[0]
                    # SEPO_id = self.tokenizer.encode('<SEPO>')[0]
                    # attn_mask_value = torch.zeros(1, 0, device=self.device)
                    # is_value = False
                    # attn_mask = torch.ones(input_ids.shape, device=self.device)
                    past = None
                    while(len(generated_sequence) < 20):
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
                        input_ids = predicted_token_tensor.view(1, 1)
                        generated_sequence.append(predicted_token_tensor)
                        if predicted_token_tensor == end_id:
                            break
                    #print(self.tokenizer.decode(generated_sequence))
                    prediction_list.append(generated_sequence)
                    distributions = [
                        distribution.cpu().numpy()
                        for distribution in distributions
                    ]
                    value, confidence = self.extract_values(
                        generated_sequence, distributions, field
                    )

                    fields_dict[field] = dict(
                        value=value.strip(),
                        confidence=np.round(np.float(confidence), 2),
                        fixed=False
                    )

                table_json.append(
                    dict(
                        id=it,
                        GSE=input_dict['GSE'],
                        GSM=input_dict['GSM'],
                        input=self.tokenizer.decode(
                            self.tokenizer.encode(
                                input_dict['input_text'].lower(),
                                truncation=True,
                                max_length=self.MAX_LEN
                            )
                        ),
                        fields=fields_dict
                    )
                )
        del self.model
        with torch.cuda.device(self.device):
            torch.cuda.empty_cache()
        return table_json

    def extract_values(self, text_ids, distributions, field):
        generated_sequence = np.array(text_ids)

        output_index = 0

        value = self.tokenizer.decode(
            generated_sequence[output_index:-1]
        )

        # confidence 1st token
        out_prob = distributions[output_index]
        confidence = np.max(out_prob)
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

        return value, confidence

    def onlineLearning(self, input_text, output_list, field_list):
        self.model = self.base_model.to(self.device)
        if path.isfile('Models/' + 'augmented_' + self.name_model):
            augmented = 'augmented_'
        else:
            augmented = ''
        self.model.load_state_dict(
            torch.load(
                'Models/' + augmented + self.name_model, map_location=self.device
            )
        )
        input_prefix = self.tokenizer.encode(
            input_text,
            return_tensors='pt',
            truncation=True,
            max_length=self.MAX_LEN
        ).to(self.device)
        for output_text, field in zip(output_list, field_list):
            print(output_text)
            output_ids = self.tokenizer.encode(
                output_text,
                return_tensors='pt'
            ).to(self.device)
            conditional_ids = self.tokenizer.encode(
                field,
                return_tensors='pt'
            ).to(self.device)
            inp_out_ids = torch.cat(
                (
                    torch.tensor([[self.tokenizer.bos_token_id]], device=self.device),
                    input_prefix,
                    torch.tensor([[self.tokenizer.sep_token_id]], device=self.device),
                    conditional_ids,
                    output_ids
                ),
                dim=-1
            )
            labels = inp_out_ids.clone().detach()
            labels[0, :-output_ids.shape[1]] = torch.ones(
                input_prefix.shape[1] + conditional_ids.shape[1] + 2
            ) * -100

            optimizer = torch.optim.Adam(self.model.parameters(), lr=2e-5)
            new_output = torch.empty(output_ids.shape, device=self.device)
            not_match = True
            max_epochs = 10
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
                            input_prefix,
                            torch.tensor(
                                [[self.tokenizer.sep_token_id]],
                                device=self.device
                            ),
                            conditional_ids
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
                    print(f'output generato per field: {field}, con output {self.tokenizer.decode(list(output_ids[0]))} e con generate sequence:', self.tokenizer.decode(list(generated_sequence[0])))
                    new_output = generated_sequence
                    if new_output.shape == output_ids.shape:
                        if torch.all(new_output.eq(output_ids)):
                            not_match = False

            # 1
        torch.save(
            self.model.state_dict(),
            'Models/' + 'augmented_' + self.name_model
        )
        del self.model
        with torch.cuda.device(self.device):
            torch.cuda.empty_cache()
        # torch.save(
        #     self.model.state_dict(),
        #     'Models/' + self.name_model_2
        # )
        # self.model.load_state_dict(
        #     torch.load('Models/' + self.name_model_2)
        # )
        # self.model.eval()
