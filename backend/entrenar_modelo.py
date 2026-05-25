import pandas as pd
import numpy as np
import pickle
import os
import warnings

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report
from xgboost import XGBClassifier

warnings.filterwarnings("ignore")

# Configuramos las rutas y variables generales
RUTA_DATASET   = "DatasetFutbolDepurado.csv" 
RUTA_MODELOS   = "datos_modelo/modelos"
os.makedirs(RUTA_MODELOS, exist_ok=True)

SELECCION_CODIGO = "ESP"
CONVOCATORIA_OBJETIVO = "Convocatoria 1 (marzo 2026)"

TODAS_CONV_HISTORIAL = [
    "Convocatoria 2 (noviembre 2025)", "Convocatoria 3 (octubre 2025)", 
    "Convocatoria 4 (septiembre 2025)", "Convocatoria 5 (junio 2025)", 
    "Convocatoria 6 (marzo 2025)", "Convocatoria 7 (noviembre 2024)", 
    "Convocatoria 8 (octubre 2024)", "Convocatoria 9 (septiembre 2024)", 
    "Convocatoria 10 (junio 2024, Eurocopa)"
]

CONV_FEATURES_5  = TODAS_CONV_HISTORIAL[:5]
CONV_FEATURES_9 = TODAS_CONV_HISTORIAL

STATS_COLS = [
    "Age", "MP", "Starts", "Min", "90s", "Gls", "Ast", "G+A", "G-PK", "PK", "PKatt",
    "CrdY", "CrdR", "G+A-PK", "Sh", "SoT", "SoT%", "Sh/90", "SoT/90", "G/Sh", "G/SoT",
    "Crs", "TklW", "Int", "Fld", "2CrdY", "Fls", "OG"
]

STATS_PORTERO_COLS = [
    "GA", "GA90", "SoTA", "Saves", "W", "D", "L", "CS", "CS%",
    "PKatt_stats_keeper", "PKA", "PKsv", "PKm"
]

# Cargamos el csv y nos quedamos solo con los jugadores españoles
def cargar_y_filtrar() -> pd.DataFrame:
    try:
        df = pd.read_csv(RUTA_DATASET, sep=";", decimal=",") 
    except FileNotFoundError:
        df = pd.read_csv(RUTA_DATASET, decimal=".")
        
    mask = df["Nation"].str.contains(SELECCION_CODIGO, na=False)
    return df[mask].copy()

# Pasamos las posiciones y ligas a variables binarias para que el modelo las entienda
def codificar_categoricas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Pos_principal"] = df["Pos"].str.split(",").str[0].str.strip()
    for pos in ["GK", "DF", "MF", "FW"]:
        df[f"pos_{pos}"] = (df["Pos_principal"] == pos).astype(int)
    
    ligas_conocidas = ['es La Liga', 'eng Premier League', 'it Serie A', 'de Bundesliga', 'fr Ligue 1']
    for liga in ligas_conocidas:
        df[f"liga_{liga.replace(' ', '_')}"] = (df["Comp"] == liga).astype(int)
    
    df["liga_Otras"] = (~df["Comp"].isin(ligas_conocidas)).astype(int)
    return df

# Juntamos las estadísticas con las convocatorias previas según el escenario
def preparar_features(df: pd.DataFrame, conv_features: list) -> tuple:
    y = (df[CONVOCATORIA_OBJETIVO] == "Sí").astype(int)

    todas_stats = STATS_COLS + STATS_PORTERO_COLS + ["Save%"]
    stats_disponibles = [c for c in todas_stats if c in df.columns]

    pos_cols  = [c for c in df.columns if c.startswith("pos_")]
    liga_cols = [c for c in df.columns if c.startswith("liga_")]

    conv_bin_cols = []
    if conv_features:
        for col in conv_features:
            if col in df.columns:
                nombre_bin = col.replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
                df[nombre_bin] = (df[col] == "Sí").astype(int)
                conv_bin_cols.append(nombre_bin)
        
        if len(conv_bin_cols) > 0:
            df["experiencia_previa"] = df[conv_bin_cols].sum(axis=1)
            conv_bin_cols.append("experiencia_previa")

    feature_cols = stats_disponibles + pos_cols + liga_cols + conv_bin_cols
    X = df[feature_cols].copy().fillna(0) 

    return X, y, feature_cols, stats_disponibles

# Calculamos cuántos aciertos tenemos en los primeros 26 jugadores
def precision_at_n(y_true, y_prob, n=26):
    indices_top_n = np.argsort(y_prob)[::-1][:n]
    return y_true.iloc[indices_top_n].sum() / n

# Definimos los 4 modelos que vamos a usar
def definir_modelos(ratio_desbalanceo):
    return {
        "rf": RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42, n_jobs=-1),
        "xgb": XGBClassifier(n_estimators=300, scale_pos_weight=ratio_desbalanceo, eval_metric="logloss", random_state=42),
        "lr": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42, solver='lbfgs'),
        "svm": SVC(probability=True, class_weight="balanced", random_state=42)
    }

# Entrenamos el modelo, calculamos el acierto y lo guardamos en un archivo .pkl
def entrenar_y_guardar(X, y, feature_cols, cols_numericas, ventana, algoritmo_nombre, modelo):
    preprocessor = ColumnTransformer(
        transformers=[('num', StandardScaler(), cols_numericas)],
        remainder='passthrough'
    )
    
    X_scaled = preprocessor.fit_transform(X)
    modelo.fit(X_scaled, y)
    
    y_prob = modelo.predict_proba(X_scaled)[:, 1]
    p_at_26 = precision_at_n(y, y_prob, n=26)
    
    nombre_archivo = f"modelo_ESP_{ventana}_{algoritmo_nombre}.pkl"
    ruta_pkl = os.path.join(RUTA_MODELOS, nombre_archivo)
    
    payload = {
        "model": modelo,
        "preprocessor": preprocessor, 
        "feature_names": feature_cols,
        "ventana": ventana
    }
    with open(ruta_pkl, "wb") as f:
        pickle.dump(payload, f)
        
    return p_at_26, modelo, preprocessor, y_prob


def main():
    print("Iniciando el entrenamiento de los modelos...")
    
    try:
        df = cargar_y_filtrar()
        print(f"Jugadores españoles cargados: {len(df)}")
    except Exception as e:
        print(f"Error leyendo el archivo: {e}")
        return

    df_codificado = codificar_categoricas(df)
    
    X_v1, y, feats_v1, num_cols = preparar_features(df_codificado, [])
    X_v2, _, feats_v2, _ = preparar_features(df_codificado, CONV_FEATURES_5)
    X_v3, _, feats_v3, _ = preparar_features(df_codificado, CONV_FEATURES_9)
    
    ratio = (y == 0).sum() / y.sum()
    
    resultados = {}
    todas_las_probabilidades = {}

    print("\nEntrenando los 12 modelos...")
    for v_nombre, X_vent, feats in [("v1_Meritocratico", X_v1, feats_v1), 
                                    ("v2_Hibrido", X_v2, feats_v2), 
                                    ("v3_Continuista", X_v3, feats_v3)]:
        modelos = definir_modelos(ratio)
        for algo_nombre, modelo in modelos.items():
            nombre_modelo = f"{v_nombre}_{algo_nombre}"
            p26, mod_entrenado, prep, y_prob = entrenar_y_guardar(X_vent, y, feats, num_cols, v_nombre, algo_nombre, modelo)
            
            resultados[nombre_modelo] = p26
            todas_las_probabilidades[nombre_modelo] = y_prob
            
    print("\n" + "="*50)
    print("Resultados de los modelos (ajuste a la convocatoria de marzo):")
    print("="*50)
    
    ruta_resultados_insample = os.path.join("datos_modelo", "resultados_convo_marzo_26.txt")
    with open(ruta_resultados_insample, "w", encoding="utf-8") as f_res:
        f_res.write("Resultados de Precision@26 (convocatoria marzo 2026)\n")
        f_res.write("="*65 + "\n")
        for nombre, p26 in sorted(resultados.items(), key=lambda x: -x[1]):
            linea = f" - {nombre:<25}: {p26:.2%}"
            print(linea)
            f_res.write(linea + "\n")
            
    print("\nModelos guardados correctamente.")

    # Generamos el informe de texto con las 12 convocatorias
    ruta_informe = os.path.join("datos_modelo", "comparativa_convocatorias.txt")
    print(f"\nGenerando informe comparativo en: {ruta_informe}...")

    with open(ruta_informe, "w", encoding="utf-8") as f:
        f.write("="*80 + "\n")
        f.write(" PREDICCIONES PARA EL MUNDIAL 2026\n")
        f.write(" Evaluado con estadísticas de la temporada actual.\n")
        f.write(" Estructura: 3 Porteros | 8 Defensas | 8 Medios | 7 Delanteros\n")
        f.write("="*80 + "\n\n")

        for nombre_modelo, prob_array in todas_las_probabilidades.items():
            f.write(f"{'*'*75}\n")
            f.write(f" MODELO: {nombre_modelo}\n")
            f.write(f"{'*'*75}\n")
            
            df_resultados = df.copy()
            df_resultados["Probabilidad_IA"] = prob_array
            df_resultados["Pos_principal"] = df_resultados["Pos"].str.split(",").str[0].str.strip()
            
            top_gk = df_resultados[df_resultados["Pos_principal"] == "GK"].sort_values(by="Probabilidad_IA", ascending=False).head(3)
            top_df = df_resultados[df_resultados["Pos_principal"] == "DF"].sort_values(by="Probabilidad_IA", ascending=False).head(8)
            top_mf = df_resultados[df_resultados["Pos_principal"] == "MF"].sort_values(by="Probabilidad_IA", ascending=False).head(8)
            top_fw = df_resultados[df_resultados["Pos_principal"] == "FW"].sort_values(by="Probabilidad_IA", ascending=False).head(7)
            
            convocatoria_26 = pd.concat([top_gk, top_df, top_mf, top_fw])
            
            f.write(f"{'#':<3} | {'JUGADOR':<22} | {'POS':<3} | {'EQUIPO':<16} | {'LIGA':<16} | {'PROB.'}\n")
            f.write("-" * 80 + "\n")
            
            for i, (_, row) in enumerate(convocatoria_26.iterrows(), 1):
                nombre = str(row['Player'])[:22]
                pos = str(row['Pos_principal'])
                equipo = str(row['Squad'])[:16]
                
                liga_sucia = str(row['Comp'])
                liga_limpia = liga_sucia.split(" ", 1)[1] if " " in liga_sucia else liga_sucia
                liga = liga_limpia[:16]
                
                prob = row['Probabilidad_IA']
                
                if i in [4, 12, 20]:
                    f.write("-" * 80 + "\n")
                    
                f.write(f"{i:<3} | {nombre:<22} | {pos:<3} | {equipo:<16} | {liga:<16} | {prob:>7.1%}\n")
            
            f.write("\n\n")

    print("Informe generado. Puedes abrir el archivo para ver los resultados.")

if __name__ == "__main__":
    main()