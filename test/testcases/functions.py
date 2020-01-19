import pandas as pd
import os


def do_merges(df: pd.DataFrame):
    id_to_color = pd.DataFrame({
        'id': list(range(1, 6)),
        'color': ['red', 'green', 'yellow', 'black', 'white']
    })

    with_colors = df.merge(id_to_color, on='id')

    df = with_colors[['color', 'age', 'name']]

    return df


def do_things(df: pd.DataFrame):
    df_copy:pd.DataFrame = df.copy()

    names = df_copy['name']

    first_name = names.sort_values().values[0]

    some_age = int(df_copy.loc[df_copy['name'] == first_name, 'age'].values[0])

    df_filtered = df_copy[df_copy['age'] > 15].copy()

    df_filtered['age'] = some_age

    df_merged = do_merges(df_filtered)

    return df_merged


if __name__ == '__main__':

    df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data.csv'))

    df = do_things(df)
