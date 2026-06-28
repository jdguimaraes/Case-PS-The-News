import pandas as pd

path = r"../Case Analista de Dados — the news [Dataset Palavritas].xlsx"
xls = pd.read_excel(path, sheet_name=None)

for name, df in xls.items():
    print("="*80)
    print(name, df.shape)
    print(df.dtypes)
    print(df.head(3))
    print("--- nulls ---")
    print(df.isna().sum())
    print("--- dup rows ---", df.duplicated().sum())
