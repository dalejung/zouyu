import pandas as pd

def deep_get(obj, key):
    temp = obj
    for bit in key.split('.'):
        bit = bit.replace('|', '')
        try:
            temp = temp[bit]
        except:
            return None
    return temp

def process_name(name):
    left = name.find('|')
    if left != -1:
        right = name.find('|', left + 1)
        return name[left+1:right]
    return name.replace('.', '_')

def obj_to_frame(objs, columns):
    data = {}
    for col in columns:
        data[col] = []

    for obj in objs:
        for col in columns:
            arr = data[col]
            arr.append(deep_get(obj, col))

    data = {process_name(k): v for k, v in data.items()}
    columns = [process_name(col) for col in columns]
    return pd.DataFrame(data, columns=columns)
