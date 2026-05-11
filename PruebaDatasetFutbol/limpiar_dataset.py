import pandas as pd
import numpy as np

# 1. CARGAR DATOS
df = pd.read_csv('DatasetFutbol.csv', sep=';', decimal=',')
df = df.dropna(subset=['Player']).reset_index(drop=True)

# Cargar equipos actuales desde tu .txt
equipos_actuales = {}
with open('Jugadores duplicados.txt', 'r', encoding='utf-8') as f:
    for linea in f:
        if ':' in linea and "NO ES REPETIDO" not in linea:
            partes = linea.replace('-', '').split(':')
            equipos_actuales[partes[0].strip()] = partes[1].strip()

# 2. IDENTIFICADOR ÚNICO (Para gestionar a los impostores y a Nico González)
def generar_id_unico(row):
    nombre = row['Player']
    # David López, Vitinha y Wesley: ID por equipo para que NO se fusionen
    if nombre in ['David López', 'Vitinha', 'Wesley']:
        return f"{nombre}_{row['Squad']}"
    # Nicolás González: El español va aparte, los argentinos se fusionan entre sí
    if nombre == 'Nicolás González':
        return "Nico_Esp" if 'ESP' in str(row['Nation']) else "Nico_Arg"
    # Resto de mortales: ID por nombre
    return nombre

df['temp_id'] = df.apply(generar_id_unico, axis=1)

# 3. PROCESO DE FUSIÓN MANTENIENDO EL ORDEN
# Usamos un diccionario ordenado para guardar los resultados según aparecen
cols_suma = ['MP', 'Starts', 'Min', 'Gls', 'Ast', 'PK', 'PKatt', 'CrdY', 'CrdR', 'Sh', 'SoT', 'Crs', 'TklW', 'Int', 'Fld', '2CrdY', 'Fls', 'OG', 'GA', 'SoTA', 'Saves', 'W', 'D', 'L', 'CS', 'PKatt_stats_keeper', 'PKA', 'PKsv', 'PKm']
resultados = {}

print("Procesando filas en orden original...")

for _, row in df.iterrows():
    pid = row['temp_id']
    
    if pid not in resultados:
        # Primera vez que vemos a este jugador en la lista: guardamos su sitio
        new_row = row.copy()
        # Actualizar equipo si está en tu lista .txt
        nombre = row['Player']
        if nombre in equipos_actuales:
            new_row['Squad'] = equipos_actuales[nombre]
            lookup = df[df['Squad'] == new_row['Squad']]['Comp'].unique()
            if len(lookup) > 0: new_row['Comp'] = lookup[0]
        
        # Preparar posiciones
        new_row['Pos_list'] = set(str(new_row['Pos']).replace(',', ' ').split())
        resultados[pid] = new_row
    else:
        # Jugador repetido: sumamos sus datos a la fila que ya teníamos arriba
        base = resultados[pid]
        for col in cols_suma:
            base[col] += row[col]
        # Añadir nuevas posiciones si las hay
        base['Pos_list'].update(str(row['Pos']).replace(',', ' ').split())

# 4. CONVERTIR A DATAFRAME FINAL
df_final = pd.DataFrame(list(resultados.values()))

# Restaurar columna Pos
df_final['Pos'] = df_final['Pos_list'].apply(lambda s: ", ".join(sorted(list(s))))

# 5. RECÁLCULOS ESTADÍSTICOS
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

# 6. LIMPIEZA Y RENUMERACIÓN FINAL
df_final = df_final.drop(columns=['temp_id', 'Pos_list'])
# Creamos el nuevo Rk respetando este orden perfecto
df_final['Rk'] = range(1, len(df_final) + 1)

# 7. GUARDAR
df_final.to_csv('DatasetFutbolDepurado.csv', index=False, decimal='.')

print(f"¡Hecho! Jugadores finales: {len(df_final)}")
print("El orden es IDÉNTICO al original de tu Excel.")