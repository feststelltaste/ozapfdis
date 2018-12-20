import glob
import pandas as pd

def load_content(glob_pattern, recursive=True, encoding="utf-8", path_column_name="path", line_column_name="line",
                 data_column_name='raw'):
    file_list = glob.glob(glob_pattern, recursive=recursive)
    dfs = []

    for file_name in file_list:
        df = pd.read_csv(file_name, sep="\n", encoding=encoding, names=['raw'])
        df = df.reset_index()
        df = df.rename(columns={"index": line_column_name})
        df[line_column_name] = df[line_column_name] + 1
        df[path_column_name] = file_name
        df = df[[path_column_name, line_column_name, data_column_name]]
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)



