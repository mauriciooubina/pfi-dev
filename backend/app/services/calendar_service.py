import os
import pandas as pd
from fastapi import HTTPException
from app.config import PROCESSED_FILE, DATA_SOURCE
from app.schemas.calendar import CalendarResponse, AppointmentResponse
from app.services.db_service import fetch_appointments_from_db
from app.services.ml_service import predict_appointment_risk

def get_calendar_data(shop_id: str, date: str = None) -> CalendarResponse:
    """Devuelve los turnos de la fecha seleccionada y calcula el riesgo de ausentismo."""
    try:
        use_postgres = (DATA_SOURCE == "POSTGRES")
        df_date = None
        all_df = None
        
        if os.path.exists(PROCESSED_FILE):
            try:
                all_df = pd.read_csv(PROCESSED_FILE)
            except Exception:
                all_df = None

        if use_postgres:
            try:
                df_date = fetch_appointments_from_db(shop_id=shop_id, date=date)
            except Exception as db_err:
                print(f"[Warning] PostgreSQL connection failed: {db_err}. Falling back to CSV mode.")
                use_postgres = False

        if not use_postgres or df_date is None or df_date.empty:
            if not os.path.exists(PROCESSED_FILE):
                raise HTTPException(
                    status_code=404, 
                    detail="Processed appointments CSV file not found. Run the ETL pipeline first."
                )
            if all_df is None:
                all_df = pd.read_csv(PROCESSED_FILE)
            df_shop = all_df[all_df['shop_id'] == shop_id.lower()].copy()
            if df_shop.empty:
                raise HTTPException(status_code=404, detail=f"No data found for shop: {shop_id}")
            target_date = date if date else str(df_shop['date'].iloc[0])
            df_date = df_shop[df_shop['date'] == target_date].copy()
            df_date = df_date.sort_values(by='start_time')
        else:
            target_date = str(df_date['date'].iloc[0])

        appointments = []
        
        for _, row in df_date.iterrows():
            risk, color, prob = predict_appointment_risk(row, all_appointments_df=all_df)
            
            # Diagnóstico explicativo basado en antecedentes y antelación
            past_apps = 0
            past_noshows = 0
            if all_df is not None and 'client_hashed' in row:
                client_hash = row['client_hashed']
                app_date = str(row.get('date', ''))
                past = all_df[
                    (all_df['client_hashed'] == client_hash) &
                    (all_df['date'] < app_date)
                ]
                if not past.empty:
                    past_apps = len(past)
                    past_noshows = int(past['target'].sum()) if 'target' in past else 0

            barber_active = bool(row.get('barber_active', True)) if not pd.isna(row.get('barber_active', True)) else True
            barber_name = str(row.get('barber_name', 'Barbero'))

            if not barber_active or 'inactivo' in barber_name.lower():
                diag = "El profesional asignado figura inactivo en el sistema."
            elif risk == "ALTO":
                if past_noshows > 1:
                    diag = f"El cliente no se presentó a {past_noshows} de sus turnos anteriores."
                elif past_noshows == 1:
                    diag = "El cliente no se presentó a su último turno."
                elif past_apps == 0:
                    diag = "Primer turno del cliente en el local (sin confirmación)."
                else:
                    diag = "Turno agendado con varios días de anticipación sin confirmar."
            elif risk == "MEDIO":
                diag = "Turno en horario concurrido pendiente de reconfirmación."
            else:
                if past_apps >= 2 and past_noshows == 0:
                    diag = "Cliente habitual con asistencia regular."
                else:
                    diag = "Reserva con bajo margen de riesgo operativo."
                
            appointments.append(
                AppointmentResponse(
                    id=int(row['id']),
                    barber_id=int(row['barber_id']) if pd.notna(row['barber_id']) else 1,
                    barber_name=barber_name,
                    date=str(row['date']),
                    start_time=str(row['start_time']),
                    end_time=str(row['end_time']),
                    service_name=str(row['service_name']) if pd.notna(row['service_name']) else "Servicio",
                    service_price=float(row['service_price']) if pd.notna(row['service_price']) else 0.0,
                    service_duration=int(row['duration']) if pd.notna(row['duration']) else 30,
                    client_hashed=str(row['client_hashed']),
                    is_self_booked=int(row['is_self_booked']),
                    target=int(row['target']) if not pd.isna(row.get('target')) else None,
                    ausentismo_risk=risk,
                    color_code=color,
                    diagnostic=diag
                )
            )
            
        return CalendarResponse(
            shop_id=shop_id,
            date=target_date,
            total_appointments=len(appointments),
            appointments=appointments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error reading calendar data ({DATA_SOURCE}): {str(e)}"
        )
