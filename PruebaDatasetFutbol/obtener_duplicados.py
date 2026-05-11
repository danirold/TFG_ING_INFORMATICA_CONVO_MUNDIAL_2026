import pandas as pd

# 1. Cargar el dataset (le decimos que está separado por punto y coma)
df = pd.read_csv('DatasetFutbol.csv', sep=';')

# Limpieza de seguridad rápida: ignorar las filas vacías del final del Excel
df = df.dropna(subset=['Player']).reset_index(drop=True)

# 2. Crear una lista vacía para guardar a los "cazados"
jugadores_repetidos = []

# 3. El Bucle "Pasito a pasito"
# Vamos desde la fila 0 hasta la penúltima (para poder mirar la de abajo sin salirnos del archivo)
for i in range(len(df) - 1):
    jugador_actual = df.loc[i, 'Player']
    jugador_debajo = df.loc[i + 1, 'Player']
    
    # Si el de esta fila se llama igual que el de la fila de abajo...
    if jugador_actual == jugador_debajo:
        # Y si aún no lo hemos apuntado en nuestra lista...
        if jugador_actual not in jugadores_repetidos:
            jugadores_repetidos.append(jugador_actual)

# 4. Mostrar el resultado por pantalla
print(f"¡Caza terminada! Hemos encontrado {len(jugadores_repetidos)} jugadores duplicados.")
print("-" * 50)

# Mostramos el nombre de los jugadores duplicados
print("Aquí tienes una muestra de los repetidos:")
for jugador in jugadores_repetidos:
    print(f"- {jugador}")