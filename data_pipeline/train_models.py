import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb

from sklearn.metrics import (
    f1_score, recall_score, precision_score, roc_auc_score,
    accuracy_score, confusion_matrix, roc_curve, auc
)
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'processed_appointments_matrix.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'backend', 'app', 'models')
PLOTS_DIR = os.path.join(BASE_DIR, 'data_pipeline', 'plots')
LATEX_IMG_DIR = '/Users/mauriciooubina/Downloads/UADE_PFI_Template-develop/images'

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(LATEX_IMG_DIR, exist_ok=True)

def load_and_preprocess_data(csv_path):
    print(f"[+] Cargando datos desde {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # 1. Limpieza de lead_time_hours (antelación)
    med_0 = df[(df['lead_time_hours'] >= 0) & (df['is_self_booked'] == 0)]['lead_time_hours'].median()
    med_1 = df[(df['lead_time_hours'] >= 0) & (df['is_self_booked'] == 1)]['lead_time_hours'].median()
    df['clean_lead_time'] = df['lead_time_hours']
    df.loc[(df['clean_lead_time'] < 0) & (df['is_self_booked'] == 0), 'clean_lead_time'] = med_0
    df.loc[(df['clean_lead_time'] < 0) & (df['is_self_booked'] == 1), 'clean_lead_time'] = med_1
    df['clean_lead_time'] = df['clean_lead_time'].fillna(med_1)
    df['clean_lead_time'] = np.clip(df['clean_lead_time'], 0, 720) # Cap en 30 días
    
    # 2. Precio de catálogo conocido al momento de reservar
    df['catalog_price'] = df['service_price'].fillna(df['price']).fillna(10000.0)
    
    # 3. Métricas acumulativas de comportamiento histórico del cliente
    df['dt'] = pd.to_datetime(df['appointment_start'])
    df = df.sort_values('dt').reset_index(drop=True)
    df['client_past_apps'] = df.groupby('client_hashed').cumcount()
    df['client_past_noshows'] = df.groupby('client_hashed')['target'].cumsum() - df['target']
    df['client_noshow_rate'] = np.where(
        df['client_past_apps'] > 0,
        df['client_past_noshows'] / df['client_past_apps'],
        0.0
    )
    df['client_is_new'] = (df['client_past_apps'] == 0).astype(int)
    
    features_num = [
        'clean_lead_time', 'catalog_price', 'duration', 'hour_of_day',
        'client_past_apps', 'client_past_noshows', 'client_noshow_rate'
    ]
    features_cat = [
        'shop_id', 'is_self_booked', 'day_of_week', 'month', 'barber_id', 'client_is_new'
    ]
    
    X = df[features_num + features_cat].copy()
    X['barber_id'] = X['barber_id'].astype(str)
    y = df['target'].values
    
    print(f"[+] Dataset procesado: {len(X)} muestras (Clase 0: {np.sum(y == 0)}, Clase 1: {np.sum(y == 1)})")
    return X, y, features_num, features_cat

def build_preprocessor(features_num, features_cat):
    num_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    cat_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    return ColumnTransformer(
        transformers=[
            ('num', num_transformer, features_num),
            ('cat', cat_transformer, features_cat)
        ]
    )

def train_and_evaluate(X, y, preprocessor):
    ratio = (len(y) - sum(y)) / sum(y)
    
    models = {
        'Regresión Logística': LogisticRegression(
            class_weight='balanced', max_iter=1000, random_state=42
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=150, class_weight='balanced', max_depth=8, random_state=42
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=150, max_depth=4, learning_rate=0.08, random_state=42
        ),
        'XGBoost': xgb.XGBClassifier(
            n_estimators=150, max_depth=4, learning_rate=0.08, scale_pos_weight=ratio,
            eval_metric='logloss', random_state=42
        )
    }
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    metrics_summary = {}
    roc_curves_data = {}
    best_cm = None
    
    print("\n[+] Iniciando Validación Cruzada Estratificada 5-Fold...")
    
    for name, clf in models.items():
        print(f"   -> Evaluando {name}...")
        f1_scores = []
        recall_scores = []
        precision_scores = []
        roc_auc_scores = []
        accuracy_scores = []
        
        y_true_all = []
        y_pred_all = []
        y_proba_all = []
        
        for fold, (train_idx, test_idx) in enumerate(skf.split(X, y), 1):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            pipe = Pipeline([
                ('prep', preprocessor),
                ('clf', clf)
            ])
            pipe.fit(X_train, y_train)
            
            y_pred = pipe.predict(X_test)
            y_proba = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, 'predict_proba') else y_pred
            
            f1_scores.append(f1_score(y_test, y_pred))
            recall_scores.append(recall_score(y_test, y_pred))
            precision_scores.append(precision_score(y_test, y_pred, zero_division=0))
            roc_auc_scores.append(roc_auc_score(y_test, y_proba))
            accuracy_scores.append(accuracy_score(y_test, y_pred))
            
            y_true_all.extend(y_test)
            y_pred_all.extend(y_pred)
            y_proba_all.extend(y_proba)
        
        metrics_summary[name] = {
            'f1_mean': float(np.mean(f1_scores)),
            'f1_std': float(np.std(f1_scores)),
            'recall_mean': float(np.mean(recall_scores)),
            'recall_std': float(np.std(recall_scores)),
            'precision_mean': float(np.mean(precision_scores)),
            'precision_std': float(np.std(precision_scores)),
            'roc_auc_mean': float(np.mean(roc_auc_scores)),
            'roc_auc_std': float(np.std(roc_auc_scores)),
            'accuracy_mean': float(np.mean(accuracy_scores)),
            'accuracy_std': float(np.std(accuracy_scores))
        }
        
        fpr, tpr, _ = roc_curve(y_true_all, y_proba_all)
        roc_curves_data[name] = (fpr, tpr, float(np.mean(roc_auc_scores)))
        
        if name == 'Gradient Boosting':
            best_cm = confusion_matrix(y_true_all, y_pred_all)
            
    return metrics_summary, roc_curves_data, best_cm, models

def plot_and_save_charts(roc_curves_data, best_cm):
    print("[+] Generando gráficos académicos...")
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # 1. Curvas ROC Comparativas
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    colors = {
        'Regresión Logística': '#64748b',
        'Random Forest': '#3b82f6',
        'Gradient Boosting': '#10b981',
        'XGBoost': '#f59e0b'
    }
    styles = {
        'Regresión Logística': '--',
        'Random Forest': '-.',
        'Gradient Boosting': '-',
        'XGBoost': ':'
    }
    
    for name, (fpr, tpr, auc_score) in roc_curves_data.items():
        ax.plot(fpr, tpr, label=f"{name} (AUC = {auc_score:.4f})", color=colors[name], linestyle=styles[name], linewidth=2.2)
        
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Clasificador Aleatorio (AUC = 0.5000)')
    ax.set_title('Comparación de Curvas ROC - Clasificadores Supervisados', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Tasa de Falsos Positivos (1 - Especificidad)', fontsize=11)
    ax.set_ylabel('Tasa de Verdaderos Positivos (Recall / Sensibilidad)', fontsize=11)
    ax.legend(loc='lower right', frameon=True, fontsize=10)
    plt.tight_layout()
    
    roc_plot_path = os.path.join(PLOTS_DIR, 'roc_curves_comparison.png')
    latex_roc_path = os.path.join(LATEX_IMG_DIR, 'roc_curves_comparison.png')
    fig.savefig(roc_plot_path)
    fig.savefig(latex_roc_path)
    plt.close(fig)
    print(f"   -> Curva ROC guardada en {roc_plot_path} y {latex_roc_path}")
    
    # 2. Matriz de Confusión del Modelo Ganador (Gradient Boosting)
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    sns.heatmap(
        best_cm, annot=True, fmt='d', cmap='Blues', cbar=False,
        xticklabels=['Asistencia (0)', 'Ausencia (1)'],
        yticklabels=['Asistencia (0)', 'Ausencia (1)'],
        ax=ax, annot_kws={'size': 13, 'fontweight': 'bold'}
    )
    ax.set_title('Matriz de Confusión Global - Gradient Boosting (5-Fold CV)', fontsize=12, fontweight='bold', pad=12)
    ax.set_xlabel('Predicción del Modelo', fontsize=11)
    ax.set_ylabel('Clase Real (Terreno)', fontsize=11)
    plt.tight_layout()
    
    cm_plot_path = os.path.join(PLOTS_DIR, 'confusion_matrix_gradient_boosting.png')
    latex_cm_path = os.path.join(LATEX_IMG_DIR, 'confusion_matrix_gradient_boosting.png')
    fig.savefig(cm_plot_path)
    fig.savefig(latex_cm_path)
    plt.close(fig)
    print(f"   -> Matriz de Confusión guardada en {cm_plot_path} y {latex_cm_path}")

def export_final_model(X, y, preprocessor):
    print("[+] Entrenando modelo final Gradient Boosting en el dataset completo...")
    final_pipeline = Pipeline([
        ('prep', preprocessor),
        ('clf', GradientBoostingClassifier(
            n_estimators=150, max_depth=4, learning_rate=0.08, random_state=42
        ))
    ])
    final_pipeline.fit(X, y)
    
    model_export_path = os.path.join(MODELS_DIR, 'gradient_boosting_model.joblib')
    joblib.dump(final_pipeline, model_export_path)
    print(f"[+] Modelo serializado exitosamente en {model_export_path}")

def main():
    X, y, features_num, features_cat = load_and_preprocess_data(DATA_PATH)
    preprocessor = build_preprocessor(features_num, features_cat)
    metrics_summary, roc_curves_data, best_cm, models = train_and_evaluate(X, y, preprocessor)
    
    # Imprimir tabla comparativa final
    print("\n========================================================================================")
    print("                      RESUMEN DE MÉTRICAS (5-FOLD STRATIFIED CV)                        ")
    print("========================================================================================")
    print(f"{'Modelo':22s} | {'F1-Score':10s} | {'Recall':10s} | {'Precisión':10s} | {'ROC-AUC':10s} | {'Exactitud':10s}")
    print("----------------------------------------------------------------------------------------")
    for name, m in metrics_summary.items():
        print(f"{name:22s} | {m['f1_mean']:.4f} ±{m['f1_std']:.2f} | {m['recall_mean']:.4f}     | {m['precision_mean']:.4f}        | {m['roc_auc_mean']:.4f}      | {m['accuracy_mean']:.4f}")
    print("========================================================================================")
    
    # Guardar métricas en JSON
    metrics_json_path = os.path.join(BASE_DIR, 'data', 'processed', 'ml_metrics_summary.json')
    with open(metrics_json_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_summary, f, indent=2, ensure_ascii=False)
    print(f"[+] Métricas exportadas a {metrics_json_path}")
    
    # Generar gráficos
    plot_and_save_charts(roc_curves_data, best_cm)
    
    # Exportar modelo ganador
    export_final_model(X, y, preprocessor)
    print("\n[✔] Proceso de entrenamiento y serialización completado con éxito.")

if __name__ == '__main__':
    main()
