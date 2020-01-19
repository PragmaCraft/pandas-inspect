import pandas as pd
import numpy as np
import os
from multiprocessing import Pool


def job(df: pd.DataFrame):
    df['age'] = df['age'] * 2
    return df


if __name__ == '__main__':
    pool = Pool(4)

    df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data.csv'))

    ids = df['id'].unique()
    id_groups = np.array_split(ids, 4)

    groups = []
    for id_group in id_groups:
        groups.append(df[df['id'].isin(id_group)])

    result = list(pool.map(job, groups))

    res_df = pd.concat(result, axis=0)
