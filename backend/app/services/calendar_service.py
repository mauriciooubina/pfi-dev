import os
import pandas as pd
from fastapi import HTTPException
from app.config import PROCESSED_FILE, DATA_SOURCE
from app.schemas.calendar import CalendarResponse, AppointmentResponse
from app.services.db_service import fetch_appointments_from_db

def get_calendar_data(shop_id: str, date: str = None) -> CalendarResponse:
    """
    Returns appointments for a specific date and shop, attaching simulated/predicted risk flags.
    Reads from PostgreSQL when DATA_SOURCE='POSTGRES' (with automatic fallback to CSV if DB is down).
    """
    try:
        use_postgres = (DATA_SOURCE == "POSTGRES")
        df_date = None
        
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
            df = pd.read_csv(PROCESSED_FILE)
            df_shop = df[df['shop_id'] == shop_id.lower()].copy()
            if df_shop.empty:
                raise HTTPException(status_code=404, detail=f"No data found for shop: {shop_id}")
            target_date = date if date else str(df_shop['date'].iloc[0])
            df_date = df_shop[df_shop['date'] == target_date].copy()
            df_date = df_date.sort_values(by='start_time')
        else:
            target_date = str(df_date['date'].iloc[0])


        appointments = []
        
        # Risk simulation/prediction rules:
        for _, row in df_date.iterrows():
            lead_time = row['lead_time_hours'] if not pd.isna(row['lead_time_hours']) else 24.0
            self_booked = row['is_self_booked'] == 1
            barber_active = bool(row['barber_active']) if not pd.isna(row['barber_active']) else True
            
            # Predict risk flag
            if not barber_active or (lead_time > 72.0 and self_booked):
                risk = "ALTO"
                color = "#ef4444" # red-500
            elif lead_time < 6.0 and self_booked:
                risk = "MEDIO"
                color = "#f59e0b" # amber-500
            else:
                risk = "BAJO"
                color = "#10b981" # emerald-500
                
            appointments.append(
                AppointmentResponse(
                    id=int(row['id']),
                    barber_id=int(row['barber_id']) if pd.notna(row['barber_id']) else 1,
                    barber_name=str(row['barber_name']) if pd.notna(row['barber_name']) else "Barbero",
                    date=str(row['date']),
                    start_time=str(row['start_time']),
                    end_time=str(row['end_time']),
                    service_name=str(row['service_name']) if pd.notna(row['service_name']) else "Servicio",
                    service_price=float(row['service_price']) if pd.notna(row['service_price']) else 0.0,
                    service_duration=int(row['duration']) if pd.notna(row['duration']) else 30,
                    client_hashed=str(row['client_hashed']),
                    is_self_booked=int(row['is_self_booked']),
                    target=int(row['target']) if not pd.isna(row['target']) else None,
                    ausentismo_risk=risk,
                    color_code=color
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

