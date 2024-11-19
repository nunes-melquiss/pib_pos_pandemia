import pandas as pd

caminho_planilha = 'data/PIB_18.11.xlsx'
df = pd.read_excel(caminho_planilha)
print(df)
