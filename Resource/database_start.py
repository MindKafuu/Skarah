import numpy as np
import pandas as pd

df = ({'name1': []
    , 'name2': []
    , 'name3': []
    , 'name4': []
    , 'name5': []
    , 'name6': []
    , 'name7': []
    , 'name8': []
    , 'name9': []
    , 'name10': []
    , 'name11': []
    , 'name12': []
    , 'name13': []
    , 'name14': []
    , 'room1': []
    , 'room2': []
    , 'room3': []
    , 'room4': []
    , 'room5': []
    , 'room6': []
    , 'room7': []
    , 'room8': []
    , 'room9': []
    , 'room10': []
    , 'room11': []
    , 'room12': []
    , 'room13': []
    , 'room14': []
    , 'address1': []
    , 'address2': []
    , 'address3': []
    , 'address4': []
    , 'address5': []
    , 'address6': []
    , 'address7': []
    , 'address8': []
    , 'address9': []
    , 'address10': []
    , 'address11': []
    , 'address12': []
    , 'address13': []
    , 'address14': []})

for i in df:
    for j in range(200):
        df[i].append(np.nan)
df = pd.DataFrame(df)

df.to_csv('database.csv')