import pandas as pd

def deep_get(obj, key):
    temp = obj
    for bit in key.split('.'):
        try:
            temp = temp[bit]
        except:
            return None
    return temp

def obj_to_frame(objs, columns):
    data = {}
    for col in columns:
        data[col] = []

    for obj in objs:
        for col in columns:
            arr = data[col]
            arr.append(deep_get(obj, col))

    data = {k.replace('.', '_'): v for k, v in data.items()}
    columns = [col.replace('.', '_') for col in columns]
    return pd.DataFrame(data, columns=columns)
