import pandas as pd

df = pd.DataFrame({
    'name': ['ahmet', 'mehmet', 'ayse', 'riza'],
    'age': [21, 23, 12, 11],
    'height': [1.82, 1.75, 1.56, 1.23]
})

n_people = df.shape[0]

names = df['name']
ages = df['age']

doubled_ages = ages * 2

df_filtered = df[df['name'].isin(['riza', 'ayse'])]

df_projected = df[['height', 'age']]

max_age = df['age'].max()

oldest_person = df.loc[df['age'] == max_age, 'name'].values[0]