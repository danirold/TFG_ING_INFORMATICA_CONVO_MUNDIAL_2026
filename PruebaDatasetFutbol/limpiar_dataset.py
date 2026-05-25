import pandas as pd
import numpy as np

# Leemos el csv y nos eliminamos las filas sin jugador
df = pd.read_csv('DatasetFutbol.csv', sep=';', decimal=',')
df = df.dropna(subset=['Player']).reset_index(drop=True)

# Usamos el txt con los equipos actualizados de los jugadores
equipos_actuales = {}
with open('Jugadores duplicados.txt', 'r', encoding='utf-8') as f:
    for linea in f:
        if ':' in linea and "NO ES REPETIDO" not in linea:
            partes = linea.replace('-', '').split(':')
            equipos_actuales[partes[0].strip()] = partes[1].strip()

# Generamos un id unico para tratar a los jugadores que se llaman igual
def generar_id_unico(row):
    nombre = row['Player']
    # Estos tres jugadores son casos de homonimia, les juntamos con su equipo para diferenciarlos
    if nombre in ['David López', 'Vitinha', 'Wesley']:
        return f"{nombre}_{row['Squad']}"
    # Caso Nico González: separamos el español (un equipo) del argentino (dos equipos)
    if nombre == 'Nicolás González':
        return "Nico_Esp" if 'ESP' in str(row['Nation']) else "Nico_Arg"
    # Para el resto, sirve su nombre
    return nombre

df['temp_id'] = df.apply(generar_id_unico, axis=1)

# Juntamos los datos de los repetidos con el orden original del excel
# Todas las columnas que hay que sumar
cols_suma = ['MP', 'Starts', 'Min', 'Gls', 'Ast', 'PK', 'PKatt', 'CrdY', 'CrdR', 'Sh', 'SoT', 'Crs', 'TklW', 'Int', 'Fld', '2CrdY', 'Fls', 'OG', 'GA', 'SoTA', 'Saves', 'W', 'D', 'L', 'CS', 'PKatt_stats_keeper', 'PKA', 'PKsv', 'PKm']
resultados = {}

for _, row in df.iterrows():
    pid = row['temp_id']
    
    if pid not in resultados:
        # Guardamos la primera fila del jugador
        new_row = row.copy()
        
        # Si el futbolista ha cambiado de equipo, usamos el equipo actual (el del .txt)
        nombre = row['Player']
        if nombre in equipos_actuales:
            new_row['Squad'] = equipos_actuales[nombre]
            lookup = df[df['Squad'] == new_row['Squad']]['Comp'].unique()
            if len(lookup) > 0: new_row['Comp'] = lookup[0]
        
        # Guardamos las posiciones del futbolista en un set
        new_row['Pos_list'] = set(str(new_row['Pos']).replace(',', ' ').split())
        resultados[pid] = new_row
    else:
        # Si el jugador está repetido, sumamos sus estadísticas a la otra fila
        base = resultados[pid]
        for col in cols_suma:
            base[col] += row[col]
        # Actualizamos sus posiciones
        base['Pos_list'].update(str(row['Pos']).replace(',', ' ').split())

df_final = pd.DataFrame(list(resultados.values()))

df_final['Pos'] = df_final['Pos_list'].apply(lambda s: ", ".join(sorted(list(s))))

# Recalculamos promedios y porcentajes
def div_s(n, d): return n / d if d > 0 else 0 

df_final['90s'] = df_final['Min'] / 90
df_final['G+A'] = df_final['Gls'] + df_final['Ast']
df_final['G-PK'] = df_final['Gls'] - df_final['PK']
df_final['G+A-PK'] = df_final.apply(lambda x: div_s(x['Gls'] + x['Ast'] - x['PK'], x['90s']), axis=1)
df_final['SoT%'] = df_final.apply(lambda x: div_s(x['SoT'], x['Sh']) * 100, axis=1)
df_final['Sh/90'] = df_final.apply(lambda x: div_s(x['Sh'], x['90s']), axis=1)
df_final['SoT/90'] = df_final.apply(lambda x: div_s(x['SoT'], x['90s']), axis=1)
df_final['G/Sh'] = df_final.apply(lambda x: div_s(x['Gls'], x['Sh']), axis=1)
df_final['G/SoT'] = df_final.apply(lambda x: div_s(x['Gls'], x['SoT']), axis=1)
df_final['GA90'] = df_final.apply(lambda x: div_s(x['GA'], x['90s']), axis=1)
df_final['Save%'] = df_final.apply(lambda x: div_s(x['Saves'], x['SoTA']) * 100, axis=1)
df_final['CS%'] = df_final.apply(lambda x: div_s(x['CS'], x['MP']) * 100, axis=1)

# Eliminamos las columnas de apoyo que ya no valen y renumeramos todo
df_final = df_final.drop(columns=['temp_id', 'Pos_list'])
df_final['Rk'] = range(1, len(df_final) + 1)

# Obtenemos el dataset actualizado
df_final.to_csv('DatasetFutbolDepurado.csv', index=False, decimal='.')

print(f"Jugadores finales: {len(df_final)}")