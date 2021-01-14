import pandas as pd
import numpy as np

import torch

from torch.utils.data import Dataset

from transformers import GPT2LMHeadModel, GPT2TokenizerFast

import pytorch_lightning as pl
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint
from GPT2_utils import generate_professor_forcing

import torch_xla.core.xla_model as xm


def compute_pr_re_acc(fields, predicted_values, target_values):
    precisions = []
    recalls = []
    accuracies = []
    for i in range(len(fields)):
        predictions = [x[i] for x in predicted_values]
        target = [x[i] for x in target_values]
        precisions.append(precision_score(target, predictions, average='macro'))
        recalls.append(recall_score(target, predictions, average='macro'))
        accuracies.append(accuracy_score(target,predictions))
    return precisions, recalls, accuracies


def extract_values(fields, text_ids, tokenizer):
    output_indexes = []
    fields[0] = fields[0][1:]
    for field in fields:
        field_tokens = np.array(tokenizer.encode(field))
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

    assert -1 not in output_indexes, 'un output è mancante'

    values = []
    for i in range(len(output_indexes)):
        if i < len(output_indexes) - 1:
            values.append(tokenizer.decode(generated_sequence[
                output_indexes[i]:output_indexes[i+1]-len(
                    tokenizer.encode(fields[i+1])
                )-2
            ]).lower())
        else:
            values.append(
                tokenizer.decode(
                    generated_sequence[output_indexes[i]:-2]
                    ).lower()
            )
    return values


class CustomDataset(Dataset):
    def __init__(self, type, tokenizer, maxlen):
        self.type = type
        # Store the contents of the file in a pandas dataframe
        df1 = pd.read_csv('Experiment_1/Data/GPT2_fixed_data/' + type + 'set.csv')
        df2 = pd.read_csv('Experiment_2/Data/GPT2_fixed_data/' + type + 'set.csv')

        df1_IO = df1[['Input', 'Output']]
        df2_IO = df2[['Input', 'Output']]

        self.df = pd.concat([df1_IO, df2_IO], ignore_index=True)

        self.maxlen = maxlen
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        inp_str = self.df.loc[index, 'Input']
        trg_str = self.df.loc[index, 'Output']

        inp_str = '<BOS> ' + inp_str + '<EOS>'

        inp_ids = self.tokenizer.encode(inp_str)
        trg_ids = self.tokenizer.encode(trg_str)
        pad_id = self.tokenizer.encode('<PAD>')[0]
        eos_id = self.tokenizer.encode('<EOS>')

        if self.type == 'test':
            src = inp_ids
            trg = trg_ids
            return torch.tensor([src, trg])
        else:
            src = inp_ids + trg_ids
            # padding the sentence to the max length
            if len(src) > self.maxlen:
                inp_ids = inp_ids[:-(len(src) - self.maxlen + 1)] + eos_id
                src = inp_ids + trg_ids

            src = src +\
                [pad_id for _ in range(self.maxlen - len(src))]
            return torch.tensor(src)


class LM(pl.LightningModule):
    def __init__(self, max_len: int = 300):
        super(LM, self).__init__()

        self.model = GPT2LMHeadModel.from_pretrained(
            'distilgpt2',
            return_dict=True
        )
        self.tokenizer = GPT2TokenizerFast.from_pretrained('distilgpt2')
        self.tokenizer.add_special_tokens(
            {
                'bos_token': '<BOS>',
                'eos_token': '<EOS>',
                'pad_token': '<PAD>'
            }
        )
        self.model.resize_token_embeddings(len(self.tokenizer))
        self.max_len = max_len

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        loss = self.model(batch, labels=batch)[0]
        self.log('train_loss', loss)
        return {'loss': loss}

    def validation_step(self, batch, batch_idx):
        loss = self.model(batch, labels=batch)[0]
        self.log('val_loss', loss)
        return {'loss': loss}

    def test_step(self, batch, batch_idx):
        inp, trg = batch
        generated_sequence = []
        predicted_token = 0

        while (predicted_token != self.tokenizer.pad_token_id and
                len(generated_sequence) < 260):

            outputs = self.model(inp)
            next_token_logits = outputs.logits[:, -1, :]
            predicted_token_tensor = torch.argmax(next_token_logits)
            inp = torch.cat(
                (inp, predicted_token_tensor.view(1, 1)),
                dim=-1
            )
            generated_sequence.append(predicted_token)

        pred_values = extract_values(
            self.fields, generated_sequence, self.tokenizer
        )
        trg_values = extract_values(
            self.fields, trg, self.tokenizer
        )
        


        self.log('test_loss', loss)

    def configure_optimizers(self):
        return torch.optim.SGD(self.parameters(), lr=0.001, momentum=0.9)

    def train_dataloader(self):
        train_dataset = CustomDataset('train', self.tokenizer, self.max_len)

        train_dataloader = torch.utils.data.DataLoader(
            train_dataset, batch_size=10, num_workers=2)
        return train_dataloader

    def val_dataloader(self):
        val_dataset = CustomDataset('validation', self.tokenizer, self.max_len)

        val_dataloader = torch.utils.data.DataLoader(
            val_dataset, batch_size=12, num_workers=2
        )
        return val_dataloader

    def test_dataloader(self):
        test_dataset = CustomDataset('test', self.tokenizer, self.max_len)
        test_dataloader = torch.utils.data.DataLoader(
            test_dataset, batch_size=1, num_workers=2
        )
        return test_dataloader


if __name__ == "__main__":
    model = LM()
    checkpoint_callback = ModelCheckpoint(
        monitor='val_loss',
        filename='checkpoint-{epoch:02d}-{val_loss:.2f}',
        save_top_k=2,
        mode='min',
    )
    trainer = Trainer(
        tpu_cores=8,
        progress_bar_refresh_rate=3,
        max_epochs=45,
        callbacks=[checkpoint_callback]
    )
    trainer.fit(model)
