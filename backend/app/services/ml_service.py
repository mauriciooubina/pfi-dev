import os
import joblib
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any, Optional

MODEL_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "models", "gradient_boosting_model.joblib")
)

_cached_model = None

def get_ml_model():
    global _cached_model
    if _cached_model is None:
        if os.path.exists(MODEL_PATH):
            try:
                _cached_model = joblib.load(MODEL_PATH)
                print(f"[+] Modelo ML cargado exitosamente desde {MODEL_PATH}")
            except Exception as e:
                print(f"[!] Error al cargar modelo ML: {e}")
                _cached_model = None
        else:
            print(f"[!] Archivo de modelo ML no encontrado en {MODEL_PATH}")
    return _cached_model

def predict_appointment_risk(
    row: pd.Series,
    all_appointments_df: Optional[pd.DataFrame] = None
) -> Tuple[str, str, float]:
    """
    Predice el nivel de riesgo de ausentismo utilizando el modelo Gradient Boosting entrenado.
    Devuelve (risk_level, color_code, probability).
    """
    model = get_ml_model()
    
    # 1. Regla de resguardo operativo: barbero inactivo es siempre riesgo ALTO
    barber_active = bool(row.get('barber_active', True)) if not pd.isna(row.get('barber_active', True)) else True
    if not barber_active:
        return "ALTO", "#ef4444", 0.99
        
    lead_time = float(row.get('lead_time_hours', 24.0)) if not pd.isna(row.get('lead_time_hours')) else 24.0
    clean_lead_time = max(0.0, min(720.0, lead_time))
    catalog_price = float(row.get('service_price', row.get('price', 10000.0))) if not pd.isna(row.get('service_price', row.get('price'))) else 10000.0
    duration = int(row.get('duration', 30)) if not pd.isna(row.get('duration')) else 30
    hour = int(row.get('hour_of_day', 14)) if not pd.isna(row.get('hour_of_day')) else 14
    shop_id = str(row.get('shop_id', 'hellfish')).lower()
    is_self_booked = int(row.get('is_self_booked', 0))
    day_of_week = int(row.get('day_of_week', 2)) if not pd.isna(row.get('day_of_week')) else 2
    month = int(row.get('month', 3)) if not pd.isna(row.get('month')) else 3
    barber_id = str(row.get('barber_id', '1'))
    
    # Métricas históricas del cliente
    client_past_apps = 0
    client_past_noshows = 0
    client_noshow_rate = 0.0
    client_is_new = 1
    
    if all_appointments_df is not None and 'client_hashed' in row and 'appointment_start' in row:
        client_hash = row['client_hashed']
        app_start = row['appointment_start']
        past = all_appointments_df[
            (all_appointments_df['client_hashed'] == client_hash) &
            (all_appointments_df['appointment_start'] < app_start)
        ]
        if not past.empty:
            client_past_apps = len(past)
            client_past_noshows = int(past['target'].sum()) if 'target' in past else 0
            client_noshow_rate = float(client_past_noshows / client_past_apps) if client_past_apps > 0 else 0.0
            client_is_new = 0

    if model is not None:
        try:
            features = pd.DataFrame([{
                'clean_lead_time': clean_lead_time,
                'catalog_price': catalog_price,
                'duration': duration,
                'hour_of_day': hour,
                'client_past_apps': client_past_apps,
                'client_past_noshows': client_past_noshows,
                'client_noshow_rate': client_noshow_rate,
                'shop_id': shop_id,
                'is_self_booked': is_self_booked,
                'day_of_week': day_of_week,
                'month': month,
                'barber_id': barber_id,
                'client_is_new': client_is_new
            }])
            
            prob = float(model.predict_proba(features)[0, 1])
            
            # Calibración de umbrales optimizada para F1
            if prob >= 0.40:
                return "ALTO", "#ef4444", round(prob, 4)
            elif prob >= 0.20:
                return "MEDIO", "#f59e0b", round(prob, 4)
            else:
                return "BAJO", "#10b981", round(prob, 4)
        except Exception as err:
            print(f"[!] Error en predicción ML: {err}")

    # Fallback heurístico si falla la inferencia
    if lead_time > 72.0 and is_self_booked:
        return "ALTO", "#ef4444", 0.75
    elif lead_time < 6.0 and is_self_booked:
        return "MEDIO", "#f59e0b", 0.35
    else:
        return "BAJO", "#10b981", 0.10
