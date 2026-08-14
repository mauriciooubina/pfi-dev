import psycopg2
import pandas as pd
from app.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def fetch_appointments_from_db(shop_id: str, date: str = None) -> pd.DataFrame:
    conn = get_db_connection()
    
    query = """
        SELECT 
            a.id,
            a.shop_id,
            a.barber_id,
            b.name AS barber_name,
            b.active AS barber_active,
            TO_CHAR(a.start_time, 'YYYY-MM-DD') AS date,
            TO_CHAR(a.start_time, 'HH24:MI') AS start_time,
            TO_CHAR(a.start_time + (s.duration || ' minutes')::interval, 'HH24:MI') AS end_time,
            s.name AS service_name,
            a.price AS service_price,
            s.duration AS duration,
            a.client_hashed,
            a.is_self_booked,
            a.lead_time_hours,
            a.target
        FROM appointments a
        LEFT JOIN barbers b ON a.shop_id = b.shop_id AND a.barber_id = b.id
        LEFT JOIN services s ON a.shop_id = s.shop_id AND a.service_id = s.id
        WHERE LOWER(a.shop_id) = LOWER(%s)
    """
    
    params = [shop_id]
    if date:
        query += " AND a.start_time::date = %s::date"
        params.append(date)
        
    query += " ORDER BY a.start_time ASC;"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def fetch_queue_metrics_from_db():
    conn = get_db_connection()
    query = "SELECT * FROM queue_metrics;"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    result = []
    for _, row in df.iterrows():
        result.append({
            "shop_id": row["shop_id"],
            "lambda_rate": float(row["lambda_val"]) if pd.notna(row["lambda_val"]) else 0.0,
            "mu_rate": float(row["mu_val"]) if pd.notna(row["mu_val"]) else 0.0,
            "servers": int(row["servers_s"]) if pd.notna(row["servers_s"]) else 1,
            "metrics": {
                "utilization": float(row["rho"]) if pd.notna(row["rho"]) else 0.0,
                "p0": float(row["p0"]) if pd.notna(row["p0"]) else 0.0,
                "Lq": float(row["lq"]) if pd.notna(row["lq"]) else 0.0,
                "Wq_hours": float(row["wq"]) if pd.notna(row["wq"]) else 0.0,
                "Wq_minutes": float(row["wq"]) * 60.0 if pd.notna(row["wq"]) else 0.0,
                "L": float(row["l_val"]) if pd.notna(row["l_val"]) else 0.0,
                "W_hours": float(row["w_val"]) if pd.notna(row["w_val"]) else 0.0,
                "W_minutes": float(row["w_val"]) * 60.0 if pd.notna(row["w_val"]) else 0.0,
                "stable": bool(row["stable"])
            }
        })
    return result
