import pandas as pd

# Leemos el dataset (separado por ;) y eliminamos las filas sin jugador
df = pd.read_csv('DatasetFutbol.csv', sep=';')
df = df.dropna(subset=['Player']).reset_index(drop=True)

# Creamos una lista para almacenar los jugadores repetidos
jugadores_repetidos = []

# Recorremos el dataset comprobando el jugador actual con el de la fila siguiente
for i in range(len(df) - 1):
    jugador_actual = df.loc[i, 'Player']
    jugador_debajo = df.loc[i + 1, 'Player']
    
    # Si encontramos una coincidencia y no está guardado, lo añadimos a la lista
    if jugador_actual == jugador_debajo:
        if jugador_actual not in jugadores_repetidos:
            jugadores_repetidos.append(jugador_actual)

# Imprimimos por pantalla el total de jugadores repetidos
print(f"Jugadores duplicados encontrados: {len(jugadores_repetidos)}")

# Mostramos el nombre de cada jugador
for jugador in jugadores_repetidos:
    print(f"- {jugador}")