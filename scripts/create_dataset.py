from GEOparse import get_GEO
import pandas as pd
import numpy as np
from tqdm import tqdm


def main():
    dataset_type = 'train'
    df = pd.read_csv('Experiment_2/Data/GPT2_fixed_data/' + dataset_type + 'set.csv')
    for index in tqdm(range(len(df))):
        if not pd.isna(df.loc[index, 'GSM']):
            try:
                gsm_data = get_GEO(geo=df.loc[index, 'GSM'], destdir='GEO')
                input_text = '[gse]: ' + (
                    ' - '.join(gsm_data.metadata['series_id'])
                    if 'series_id' in gsm_data.metadata.keys()
                    else ''
                )
                input_text += ' [title]: ' + (
                    ' - '.join(gsm_data.metadata['title'])
                    if 'title' in gsm_data.metadata.keys()
                    else ''
                )
                input_text += ' [sample type]: ' + (
                    ' - '.join(gsm_data.metadata['type'])
                    if 'type' in gsm_data.metadata.keys()
                    else ''
                )
                input_text += ' [source name]: ' + (
                    ' - '.join(gsm_data.metadata['source_name_ch1'])
                    if 'source_name_ch1' in gsm_data.metadata.keys()
                    else ''
                )
                input_text += '[organism]: ' + (
                    ' - '.join(gsm_data.metadata['organism_ch1'])
                    if 'organism_ch1' in gsm_data.metadata.keys()
                    else ''
                )
                input_text += ' [characteristics]: ' + (
                    ' - '.join(gsm_data.metadata['characteristics_ch1'])
                    if 'characteristics_ch1' in gsm_data.metadata.keys()
                    else ''
                )
                input_text += ' [description]: ' + (
                    ' - '.join(gsm_data.metadata['description'])
                    if 'description' in gsm_data.metadata.keys()
                    else ''
                )
                input_text += ' = '
                input_text = input_text.replace('_', ' ').replace('*', '')
                input_text_words = input_text.split(' ')
                input_text_words = [
                    word if len(word) < 30 else '' for word in input_text_words
                ]
                input_text = ' '.join(input_text_words)
                df.loc[index, 'Input'] = input_text
            except:
                df.loc[index, 'GSM'] = np.nan

    df.to_csv('Experiment_2/Data/GPT2_fixed_data/' + dataset_type + 'set' + '_v2_' + '.csv')


if __name__ == '__main__':
    main()
