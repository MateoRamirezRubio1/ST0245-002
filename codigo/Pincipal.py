import networkx as nx
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt

#Cargar datos y creación de diccionarios
df_calles = pd.read_csv("calles_de_medellin_con_acoso.csv",sep=';')
df_calles['geometry'] = df_calles['geometry'].apply(wkt.loads)
df_calles = gpd.GeoDataFrame(df_calles)

area = pd.read_csv('poligono_de_medellin.csv',sep=';')
area['geometry'] = area['geometry'].apply(wkt.loads)
area = gpd.GeoDataFrame(area)

df_names = df_calles.drop(['destination', 'length', 'oneway', 'harassmentRisk', 'geometry'], axis=1)

table_names = dict()
table_datos_grafoNX_camino_corto = dict()
table_datos_camino_menor_acoso = dict()
lista_camino_corto = []
lista_camino_menor_acoso = []

# Hallar el promedio de acoso para rellenar campos vacios
promedio_acoso = 0
contador = 0
for i in range(len(df_calles)):
    if not pd.isna(df_calles['harassmentRisk'][i]):
        promedio_acoso += df_calles['harassmentRisk'][i]
        contador += 1
promedio_acoso /= contador

# Rellenar campos vacios de los dataframes
for i in range(len(df_calles['origin'])):
    #Los niveles de acoso vacíos con el promedio de acoso ponderado
    if pd.isna((df_calles['harassmentRisk'][i])):
        df_calles.at[i, 'harassmentRisk'] = promedio_acoso
    #Las calles que no tienen dato de su distancia se pone con 0
    if pd.isna((df_calles['length'][i])):
        df_calles.at[i, 'length'] = 0
    #Los nombres vacíos se pone el número de indice
    if pd.isna((df_names['name'][i])):
        df_names.at[i, 'name'] = str(i)
    #Se ponen los datos del nombre con su respectivo origen en el diccionario para ser mostrados al usuario
    table_names[df_names['name'][i]] = df_names['origin'][i]

#Mostrar datos al usuario y obtener el orgien y el destino al que se dirige
print("Calles Medellín:")
print("__________________________________")
print(df_names)
print("__________________________________")
print("A donde te quieres dirigir?: (Escriba el nombre de la calle tal cual está en la tabla)")
user_option_origin = str(input("Origen: "))
user_option_destination = str(input("Destino: "))

if (user_option_origin in table_names) and (user_option_destination in table_names):
    # Crear el grafo del camino más corto
    MAP_PATH = nx.from_pandas_edgelist(df_calles, source='origin', target='destination', edge_attr='length')
    djk_path = nx.dijkstra_path(MAP_PATH, source=table_names[user_option_origin], target=table_names[user_option_destination], weight='length')
    djk_path_length = nx.dijkstra_path_length(MAP_PATH, source=table_names[user_option_origin], target=table_names[user_option_destination], weight='length')

    # Crear el grafo del camino con menor acoso
    MAP_RISK = nx.from_pandas_edgelist(df_calles, source='origin', target='destination', edge_attr='harassmentRisk')
    djk_path_harassment = nx.dijkstra_path(MAP_RISK, source=table_names[user_option_origin], target=table_names[user_option_destination], weight='harassmentRisk')
    djk_path_harassment_length = nx.dijkstra_path_length(MAP_RISK, source=table_names[user_option_origin], target=table_names[user_option_destination], weight='harassmentRisk')

    # Hallar promedios de loas caminos para las muestras
    promedio_distancia = 0
    promedio_acoso = 0
    # Promedio distancia
    for i in djk_path:
        promedio_distancia += 1
    promedio_distancia = djk_path_length / promedio_distancia
    # Promedio acoso
    for i in djk_path_harassment:
        promedio_acoso += 1
    promedio_acoso = djk_path_harassment_length / promedio_acoso

    #Imprimir en pantalla resultados
    print("\nEsta es la ruta más corta por seguir:")
    print(djk_path)
    print("Distancia total: ", djk_path_length)
    print("Promedio distancia del camino:", promedio_distancia)
    print("\nEsta es la ruta con menor acoso por seguir:")
    print(djk_path_harassment)
    print("Valor total acoso: ", djk_path_harassment_length)
    print("Promedio acoso del camino:", promedio_acoso)

    # Llenar los diccionarios con los origenes obtenidos
    # Origenes camino más corto
    for i in djk_path:
        table_datos_grafoNX_camino_corto[i] = 0
    # Origenes camino con menor acoso
    for i in djk_path_harassment:
        table_datos_camino_menor_acoso[i] = 0

    # Obtener las coordenadas de los origenes anteriormente obtenidos
    for i in range(len(df_calles)):
        if df_calles['origin'][i] in table_datos_grafoNX_camino_corto:
            lista_camino_corto.append(str(df_calles['geometry'][i]))
        if df_calles['origin'][i] in table_datos_camino_menor_acoso:
            lista_camino_menor_acoso.append(str(df_calles['geometry'][i]))

    # Crear dataframes pandas con las coordenadas anteriormente obtenidas para graficar los caminos
    data_camino_corto = pd.DataFrame(lista_camino_corto, columns=['geometry'])
    data_camino_corto['geometry'] = data_camino_corto['geometry'].apply(wkt.loads)
    data_camino_corto = gpd.GeoDataFrame(data_camino_corto)

    data_camino_menor_acoso = pd.DataFrame(lista_camino_menor_acoso, columns=['geometry'])
    data_camino_menor_acoso['geometry'] = data_camino_menor_acoso['geometry'].apply(wkt.loads)
    data_camino_menor_acoso = gpd.GeoDataFrame(data_camino_menor_acoso)

    # Graficar mapa Medellín con el camino más corto
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(20, 12))
    # Graficar fondo
    area.plot(ax=ax, facecolor='black')
    # Graficar calles Medellín
    df_calles.plot(ax=ax, linewidth=1, edgecolor='dimgray')
    # Graficar camino más corto
    data_camino_corto.plot(ax=ax, linewidth=1, edgecolor='darkorange')
    # Mostrar mapa con camino mas corto
    plt.title(f'Camino Más Corto\n Distancia total: {djk_path_length}\n Promedio dsitancia del camino: {promedio_distancia}')
    plt.tight_layout()
    plt.show()

    # Graficar mapa Medellín con el camino con menor acoso
    # Crear gráfico
    fig, ax = plt.subplots(figsize=(20, 12))
    # Graficar fondo
    area.plot(ax=ax, facecolor='black')
    # Graficar calles Medellín
    df_calles.plot(ax=ax, linewidth=1, edgecolor='dimgray')
    # Graficar camino con menor acoso
    data_camino_menor_acoso.plot(ax=ax, linewidth=1, edgecolor='darkorange')
    # Mostrar mapa camino con menor acoso
    plt.title(f'Camino Con Menor Acoso\n Valor total acoso: {djk_path_harassment_length}\n Promedio acoso del camino: {promedio_acoso}')
    plt.tight_layout()
    plt.show()
else:
    if not (user_option_origin in table_names):
        print("El origen ingresado no se encuentra en la tabla. Vuelva a intentarlo.")
    if not (user_option_destination in table_names):
        print("El destino ingresado no se encuentra en la tabla. Vuelva a intentarlo.")
