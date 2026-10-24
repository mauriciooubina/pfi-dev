import os
import pandas as pd
from fastapi import HTTPException
from app.config import PROCESSED_FILE, DATA_SOURCE
from app.schemas.calendar import CalendarResponse, AppointmentResponse, SimulateAppointmentRequest
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

def simulate_appointment_service(req: SimulateAppointmentRequest) -> AppointmentResponse:
    """
    Simula en caliente un nuevo turno, evaluándolo mediante el modelo Gradient Boosting
    según el perfil de cliente seleccionado para la prueba en vivo.
    Calcula la antelación real contra el momento actual de la reserva (datetime.now()).
    """
    try:
        from datetime import datetime, timedelta
        import hashlib
        import random

        now = datetime.now()
        start_time_str = req.start_time if len(req.start_time) == 8 else f"{req.start_time[:5]}:00"
        
        # Cálculo de antelación real respecto a ahora
        try:
            app_dt = datetime.strptime(f"{req.date} {start_time_str}", "%Y-%m-%d %H:%M:%S")
            delta_hours = (app_dt - now).total_seconds() / 3600.0
            if delta_hours > 0:
                lead_time = round(delta_hours, 1)
            elif req.lead_time_hours is not None and req.lead_time_hours > 0:
                lead_time = float(req.lead_time_hours)
            else:
                lead_time = 1.0  # Turno inmediato / sobre la hora
        except Exception:
            lead_time = float(req.lead_time_hours) if (req.lead_time_hours and req.lead_time_hours > 0) else 24.0

        profile = req.client_profile.lower()

        if profile in ("franco", "fiel"):
            client_name = req.client_name or "Franco Martínez"
            client_hash = hashlib.sha256(b"CLIENTE_FRANCO_MARTINEZ").hexdigest()[:16]
            client_past_apps = 12
            client_past_noshows = 0
            client_noshow_rate = 0.0
            client_is_new = 0
            diag = f"Cliente habitual ({client_name}): 12 turnos asistidos sin faltas (0% ausentismo). Mínimo margen de riesgo estocástico."
        elif profile in ("matias",):
            client_name = req.client_name or "Matías Giménez"
            client_hash = hashlib.sha256(b"CLIENTE_MATIAS_GIMENEZ").hexdigest()[:16]
            client_past_apps = 4
            client_past_noshows = 2
            client_noshow_rate = 0.50
            client_is_new = 0
            diag = f"Cliente ocasional ({client_name}): 2 inasistencias sobre 4 turnos (50% ausentismo). Riesgo sensible a la antelación de reserva ({lead_time:.0f}h)."
        elif profile in ("tomas", "nuevo"):
            client_name = req.client_name or "Tomás Rodríguez"
            client_hash = hashlib.sha256(b"CLIENTE_TOMAS_RODRIGUEZ").hexdigest()[:16]
            client_past_apps = 0
            client_past_noshows = 0
            client_noshow_rate = 0.0
            client_is_new = 1
            diag = f"Cliente nuevo ({client_name}): primer turno agendado en el local (sin historial previo). Incertidumbre moderada."
        else:  # "gonzalo" o "riesgo"
            client_name = req.client_name or "Gonzalo Castro"
            client_hash = hashlib.sha256(b"CLIENTE_GONZALO_CASTRO").hexdigest()[:16]
            client_past_apps = 4
            client_past_noshows = 3
            client_noshow_rate = 0.75
            client_is_new = 0
            diag = f"Alerta predictiva ({client_name}): 3 inasistencias sobre 4 turnos (75% ausentismo histórico). Alto riesgo de inasistencia."

        duration = req.service_duration if req.service_duration > 0 else 30
        price = req.service_price if req.service_price > 0 else 18000.0

        try:
            st_dt = datetime.strptime(start_time_str, "%H:%M:%S")
            et_dt = st_dt + timedelta(minutes=duration)
            end_time_str = et_dt.strftime("%H:%M:%S")
            hour_of_day = st_dt.hour
        except Exception:
            end_time_str = "16:30:00"
            hour_of_day = 16

        try:
            date_dt = datetime.strptime(req.date, "%Y-%m-%d")
            day_of_week = date_dt.weekday()
            month = date_dt.month
        except Exception:
            day_of_week = 2
            month = 10

        simulated_row = pd.Series({
            'shop_id': req.shop_id.lower(),
            'barber_id': str(req.barber_id),
            'barber_active': True,
            'lead_time_hours': lead_time,
            'service_price': price,
            'duration': duration,
            'hour_of_day': hour_of_day,
            'is_self_booked': req.is_self_booked,
            'day_of_week': day_of_week,
            'month': month,
            'client_hashed': client_hash,
            'appointment_start': f"{req.date} {start_time_str}"
        })

        virtual_past_records = []
        for i in range(client_past_apps):
            virtual_past_records.append({
                'client_hashed': client_hash,
                'date': '2026-09-01',
                'appointment_start': '2026-09-01 10:00:00',
                'target': 1 if i < client_past_noshows else 0
            })
        virtual_past_df = pd.DataFrame(virtual_past_records) if virtual_past_records else None

        risk, color, prob = predict_appointment_risk(simulated_row, all_appointments_df=virtual_past_df)

        simulated_id = 9000 + random.randint(100, 999)

        return AppointmentResponse(
            id=simulated_id,
            barber_id=req.barber_id,
            barber_name=req.barber_name or "Profesional",
            date=req.date,
            start_time=start_time_str,
            end_time=end_time_str,
            service_name=req.service_name,
            service_price=price,
            service_duration=duration,
            client_hashed=client_name,
            is_self_booked=req.is_self_booked,
            target=None,
            ausentismo_risk=risk,
            color_code=color,
            diagnostic=diag
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en simulación en tiempo real: {str(e)}"
        )

