import pandas as pd

print("Pandas calles de Medellín:\n")
df_calles = pd.read_csv("calles_de_medellin_con_acoso.csv",sep=';')
print(df_calles)

print("\n\nPandas polígono de Medellín:\n")
df_poligono = pd.read_csv("poligono_de_medellin.csv",sep=';')
print(df_poligono)
