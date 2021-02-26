import pandas as pd
from tqdm import tqdm


def main():
    dataset_type = 'train'
    df = pd.read_csv(
        'Experiment_2/Data/GPT2_fixed_data/'
        + dataset_type + 'set' + '_v2_' + '.csv'
        )

    for index in tqdm(range(len(df))):
        output_text = df.loc[index, 'Output']
        output_fields = output_text.split(' - ')
        assert len(output_fields) == 15, (
            f'un output ha dei dash interni {output_fields}'
        )
        output_text = output_text.replace(' - ', '<SEPO>')
        output_text = output_text.replace(' $', '<EOS>')
        df.loc[index, 'Output'] = output_text
        input_text = df.loc[index, 'Input']
        assert input_text[-3:] == ' = ', (
            f'il finale di un input non è corretto {input_text[:-6]}'
        )
        input_text = input_text[:-3] + '<SEP>'
        input_text = '<BOS>' + input_text
        df.loc[index, 'Input'] = input_text
    df.to_csv(
        'Experiment_2/Data/GPT2_fixed_data/'
        + dataset_type + 'set' + '_v3_' + '.csv'
    )


if __name__ == '__main__':
    main()
