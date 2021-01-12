import os
import pickle
import argparse
import time
import glob

import numpy as np
from tqdm import tqdm
import pandas as pd

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pad_sequence

from torch.optim import SGD

from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import Dataset

from transformers import GPT2LMHeadModel, CTRLLMHeadModel, GPT2TokenizerFast, CTRLTokenizer, AdamW, get_linear_schedule_with_warmup

import pytorch_lightning as pl
from pytorch_lightning import Trainer
from pytorch_lightning.callbacks import ModelCheckpoint

import torch_xla.core.xla_model as xm


class CustomDataset(Dataset):
    def __init__(self, type, tokenizer, maxlen):

        # Store the contents of the file in a pandas dataframe
        df1 = pd.read_csv('Experiment_1/Data/GPT2_fixed_data/' + type + 'set.csv')
        df2 = pd.read_csv('Experiment_2/Data/GPT2_fixed_data/' + type + 'set.csv')

        df1_IO = df1[['Input', 'Output']]
        df2_IO = df2[['Input', 'Output']]

        self.df = pd.concat([df1_IO, df2_IO], ignore_index=True)

        self.maxlen = maxlen
        self.tokenizer = tokenizer
        self.n_cuts = 0

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

        src = inp_ids + trg_ids

        # padding the sentence to the max length
        if len(src) > self.maxlen:
            inp_ids = inp_ids[:-(len(src) - self.maxlen + 1)] + eos_id
            src = inp_ids + trg_ids
            self.n_cuts += 1

        src = src +\
            [pad_id for _ in range(self.maxlen - len(src))]
        return torch.tensor(src)


class LM(pl.LightningModule):
    def __init__(self, max_len: int = 300):
        super(LM, self).__init__()

        ######### CHANGED ##########
        self.model = GPT2LMHeadModel.from_pretrained('distilgpt2')
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
        val_dataset, batch_size=12, num_workers=2)

        return val_dataloader


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