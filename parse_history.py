import pandas as pd

df = pd.read_csv('results/history.csv')
print(df)

# for i, row in df.iterrows():
#     print(i, row[:-2].sum())

count = 0
for i, row in enumerate(df.dices):
    if row == ['pd', 'pd', 'pd']:
        print(i)
        count += 1
if count == 0:
    print("No powerdots")