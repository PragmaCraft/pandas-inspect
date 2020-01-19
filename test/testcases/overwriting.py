import os

import pandas as pd


def func(df):
    df['height_age_ind'] = df['age'] / df['height']

    df['height_age_ind'] = df['height_age_ind'] ** 2

    df['just_ones'] = 1

    df = df[(df['height_age_ind'] > df['height_age_ind'].mean())]

    return df


df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data.csv'))

df = func(df)