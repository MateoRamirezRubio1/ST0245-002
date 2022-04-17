import pandas as pd
from collections import defaultdict

class Vertice:
    def __init__(self, i):
        self.id = i
        self.vecinos = []
        self.visitado = False
        self.padre = None
        self.distancia = float('inf')

    def agregarVecino(self, v, p):
        if v not in self.vecinos:
            self.vecinos.append([v, p])

class Grafica:
    def __init__(self):
        self.vertices = {}

    def agregarVertice(self, id):
        if id not in self.vertices:
            self.vertices[id] = Vertice(id)

    def agregarArista(self, a , b, p):
        if a in self.vertices and b in self.vertices:
            self.vertices[a].agregarVecino(b, p)
            self.vertices[b].agregarVecino(a, p)

    def camino(self, a, b):
        camino = []
        actual = b
        while actual != None:
            camino.insert(0, actual)
            actual = self.vertices[actual].padre
        return [camino, self.vertices[b].distancia]

    def minimo(self, lista):
        if len(lista) > 0:
            m = self.vertices[lista[0]].distancia
            v = lista[0]
            for e in lista:
                if m > self.vertices[e].distancia:
                    m = self.vertices[e].distancia
                    v = e

            return v

    def dijkstra(self, a):
        if a in self.vertices:
            self.vertices[a].distancia = 0
            actual = a
            noVisitados = []

            for v in self.vertices:
                if v != a:
                    self.vertices[v].distancia = float('inf')
                self.vertices[v].padre = None
                noVisitados.append(v)

            while len(noVisitados) > 0:
                for vecino in self.vertices[actual].vecinos:
                    if self.vertices[vecino[0]].visitado == False:
                        if self.vertices[actual].distancia + vecino[1] < self.vertices[vecino[0]].distancia:
                            self.vertices[vecino[0]].distancia = self.vertices[actual].distancia + vecino[1]
                            self.vertices[vecino[0]].padre = actual

                self.vertices[actual].visitado = True
                noVisitados.remove(actual)

                actual = self.minimo(noVisitados)
        else:
            return False

class main:

    #La ejecución del programa

    # Cargar datos y crear diccionarios
    df_calles = pd.read_csv("calles_de_medellin_con_acoso.csv", sep=';')
    df_names = df_calles.drop(['destination', 'length', 'oneway', 'harassmentRisk', 'geometry'], axis=1)
    df_calles = df_calles.drop(['name', 'oneway', 'geometry'], axis=1)
    table = defaultdict(lambda: "No se presenta")  # Diccionario con los datos de cada calle
    table_names = defaultdict(lambda: "No se encuentra esta calle")  # Diccionario para obtener el dato ingresado por el usuario

    # Crear tabla para los nombres de las calles
    for i in range(len(df_names['name'])):
        if pd.isna((df_names['name'][i])):
            df_names.at[i, 'name'] = df_names['origin'][i]
        table_names[df_names['name'][i]] = df_names['origin'][i]

    # Rellenar espacios vacios de los dataframes
    for i in range(len(df_calles['origin'])):
        if pd.isna((df_calles['harassmentRisk'][i])):
            df_calles.at[i, 'harassmentRisk'] = 0
        if pd.isna((df_calles['length'][i])):
            df_calles.at[i, 'length'] = 0

    # Introducir datos al diccionario correspondiente (creación lista de adyacencia)
    for i in range(len(df_calles["origin"])):
        if df_calles["origin"][i] in table:
            table[str(df_calles["origin"][i])] += [
                (df_calles["destination"][i], df_calles["length"][i], df_calles["harassmentRisk"][i])]
        else:
            table[str(df_calles["origin"][i])] = [(df_calles["destination"][i], df_calles["length"][i], df_calles["harassmentRisk"][i])]

    # Pedir datos al usuario
    print("Calles Medellín:")
    print("__________________________________")
    print(df_names)
    print("__________________________________")
    print("A donde te quieres dirigir?: (Escriba el nombre de la calle tal cual está en la tabla)")
    user_option_origin = str(input("Origen: "))
    user_option_destination = str(input("Destino: "))

    # Crear grafos
    grafo_camio_corto = Grafica()
    grafo_menor_acoso = Grafica()
    boolean = False
    for i in table:
        grafo_camio_corto.agregarVertice(i)
        grafo_menor_acoso.agregarVertice(i)
        a = len(table[i])
        while a > 0:
            grafo_camio_corto.agregarArista(i, table[i][a - 1][0], table[i][a - 1][1])
            grafo_menor_acoso.agregarArista(i, table[i][a - 1][0], table[i][a - 1][2])
            a -= 1

    # Ejecutar algoritmo
    grafo_camio_corto.dijkstra(table_names[user_option_origin])
    grafo_menor_acoso.dijkstra(table_names[user_option_origin])

    # Imprimir algoritmo
    grafo_CO = grafo_camio_corto.camino(table_names[user_option_origin], table_names[user_option_destination])
    grafo_MA = grafo_menor_acoso.camino(table_names[user_option_origin], table_names[user_option_destination])
    if grafo_MA[1] == float('inf') or grafo_CO[1] == float('inf'):
        print("La ruta seleccionada no es transitable")
    else:
        print("Ruta con menor acoso:")
        print(grafo_MA[0])
        print("Acoso total:", end=" ")
        print(grafo_MA[1])
        print("\nRuta más corta:")
        print(grafo_CO[0])
        print("Distancia total:", end=" ")
        print(grafo_CO[1])
