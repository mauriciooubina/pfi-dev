import os
import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "pfi_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

CREATE_TABLES_SQL = """
DROP TABLE IF EXISTS appointments CASCADE;
DROP TABLE IF EXISTS consolidated_blocks CASCADE;
DROP TABLE IF EXISTS barbers CASCADE;
DROP TABLE IF EXISTS services CASCADE;
DROP TABLE IF EXISTS queue_metrics CASCADE;

CREATE TABLE barbers (
    id VARCHAR(50) NOT NULL,
    shop_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    commission NUMERIC(5,2),
    PRIMARY KEY (shop_id, id)
);

CREATE TABLE services (
    id VARCHAR(50) NOT NULL,
    shop_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price NUMERIC(10,2),
    duration INT,
    PRIMARY KEY (shop_id, id)
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    raw_appointment_id VARCHAR(50),
    shop_id VARCHAR(50) NOT NULL,
    barber_id VARCHAR(50),
    service_id VARCHAR(50),
    client_hashed VARCHAR(64),
    phone_hashed VARCHAR(64),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    price NUMERIC(10,2),
    paid BOOLEAN DEFAULT FALSE,
    is_self_booked INT,
    day_of_week INT,
    hour_of_day INT,
    month INT,
    lead_time_hours NUMERIC(10,2),
    cancelation_margin_hours NUMERIC(10,2),
    target INT,
    created_at TIMESTAMP,
    created_by VARCHAR(100),
    deleted_at TIMESTAMP,
    deleted_by VARCHAR(100)
);

CREATE TABLE consolidated_blocks (
    id SERIAL PRIMARY KEY,
    shop_id VARCHAR(50) NOT NULL,
    barber_id VARCHAR(50),
    service_id VARCHAR(50),
    client VARCHAR(100),
    phone VARCHAR(50),
    date VARCHAR(20),
    start_time VARCHAR(20),
    end_time VARCHAR(20),
    price NUMERIC(10,2),
    paid VARCHAR(20),
    created_at VARCHAR(50),
    created_by VARCHAR(100),
    deleted_at VARCHAR(50),
    deleted_by VARCHAR(100)
);

CREATE TABLE queue_metrics (
    id SERIAL PRIMARY KEY,
    shop_id VARCHAR(50) NOT NULL,
    date VARCHAR(20),
    lambda_val NUMERIC(10,4),
    mu_val NUMERIC(10,4),
    servers_s INT,
    rho NUMERIC(10,4),
    lq NUMERIC(10,4),
    wq NUMERIC(10,4),
    l_val NUMERIC(10,4),
    w_val NUMERIC(10,4),
    p0 NUMERIC(10,4),
    stable BOOLEAN
);
"""

def populate_database(base_dir):
    conn = get_db_connection()
    cur = conn.cursor()

    print("Dropping old tables and creating new schema...")
    cur.execute(CREATE_TABLES_SQL)
    conn.commit()

    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")

    shops = ["hellfish", "hooligans"]

    # 1. Populate Barbers & Services metadata
    for shop in shops:
        shop_raw_dir = os.path.join(raw_dir, shop)
        barbers_path = os.path.join(shop_raw_dir, "barbers.csv")
        services_path = os.path.join(shop_raw_dir, "services.csv")

        if os.path.exists(barbers_path):
            df_b = pd.read_csv(barbers_path)
            barber_tuples = [
                (
                    str(r['id']), shop, str(r['name']),
                    str(r['role']) if pd.notna(r.get('role')) else None,
                    bool(r['active']) if pd.notna(r.get('active')) else True,
                    float(r['commission']) if pd.notna(r.get('commission')) else None
                ) for _, r in df_b.iterrows()
            ]
            execute_values(cur, """
                INSERT INTO barbers (id, shop_id, name, role, active, commission)
                VALUES %s
                ON CONFLICT (shop_id, id) DO NOTHING;
            """, barber_tuples)

        if os.path.exists(services_path):
            df_s = pd.read_csv(services_path)
            service_tuples = [
                (
                    str(r['id']), shop, str(r['name']),
                    str(r.get('description', '')) if pd.notna(r.get('description')) else None,
                    float(r['price']) if pd.notna(r.get('price')) else 0.0,
                    int(r['duration']) if pd.notna(r.get('duration')) else 30
                ) for _, r in df_s.iterrows()
            ]
            execute_values(cur, """
                INSERT INTO services (id, shop_id, name, description, price, duration)
                VALUES %s
                ON CONFLICT (shop_id, id) DO NOTHING;
            """, service_tuples)

    print("Populated barbers and services tables.")

    # 2. Populate Processed Appointments Matrix
    matrix_path = os.path.join(processed_dir, "processed_appointments_matrix.csv")
    if os.path.exists(matrix_path):
        df_app = pd.read_csv(matrix_path)
        app_tuples = [
            (
                str(r.get('id', '')), str(r.get('shop_id', '')),
                str(r.get('barber_id', '')), str(r.get('service_id', '')),
                str(r.get('client_hashed', '')), str(r.get('phone_hashed', '')),
                str(r['appointment_start']) if pd.notna(r.get('appointment_start')) else None,
                None,
                float(r['price']) if pd.notna(r.get('price')) else 0.0,
                bool(r['paid']) if pd.notna(r.get('paid')) else False,
                int(r['is_self_booked']) if pd.notna(r.get('is_self_booked')) else 0,
                int(r['day_of_week']) if pd.notna(r.get('day_of_week')) else 0,
                int(r['hour_of_day']) if pd.notna(r.get('hour_of_day')) else 0,
                int(r['month']) if pd.notna(r.get('month')) else 0,
                float(r['lead_time_hours']) if pd.notna(r.get('lead_time_hours')) else 0.0,
                float(r['cancelation_margin_hours']) if pd.notna(r.get('cancelation_margin_hours')) else None,
                int(r['target']) if pd.notna(r.get('target')) else 0,
                str(r['created_at']) if pd.notna(r.get('created_at')) else None,
                str(r['created_by']) if pd.notna(r.get('created_by')) else None,
                str(r['deleted_at']) if pd.notna(r.get('deleted_at')) else None,
                str(r['deleted_by']) if pd.notna(r.get('deleted_by')) else None,
            ) for _, r in df_app.iterrows()
        ]
        execute_values(cur, """
            INSERT INTO appointments (
                raw_appointment_id, shop_id, barber_id, service_id,
                client_hashed, phone_hashed, start_time, end_time, price, paid,
                is_self_booked, day_of_week, hour_of_day, month,
                lead_time_hours, cancelation_margin_hours, target,
                created_at, created_by, deleted_at, deleted_by
            ) VALUES %s;
        """, app_tuples, page_size=1000)
        print(f"Populated appointments table with {len(df_app)} rows.")

    # 3. Populate Consolidated Blocks
    blocks_path = os.path.join(processed_dir, "consolidated_blocks.csv")
    if os.path.exists(blocks_path):
        df_blocks = pd.read_csv(blocks_path)
        block_tuples = [
            (
                str(r.get('shop_id', '')), str(r.get('barber_id', '')), str(r.get('service_id', '')),
                str(r.get('client', '')), str(r.get('phone', '')), str(r.get('date', '')),
                str(r.get('start_time', '')), str(r.get('end_time', '')),
                float(r['price']) if pd.notna(r.get('price')) else 0.0,
                str(r.get('paid', '')), str(r.get('created_at', '')), str(r.get('created_by', '')),
                str(r.get('deleted_at', '')), str(r.get('deleted_by', ''))
            ) for _, r in df_blocks.iterrows()
        ]
        execute_values(cur, """
            INSERT INTO consolidated_blocks (
                shop_id, barber_id, service_id, client, phone, date,
                start_time, end_time, price, paid, created_at, created_by, deleted_at, deleted_by
            ) VALUES %s;
        """, block_tuples, page_size=1000)
        print(f"Populated consolidated_blocks table with {len(df_blocks)} rows.")

    # 4. Populate Queue Metrics
    metrics_path = os.path.join(processed_dir, "queue_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            q_data = json.load(f)
            metric_tuples = []
            for item in q_data:
                s_id = item.get("shop_id")
                l_rate = item.get("lambda_rate")
                m_rate = item.get("mu_rate")
                serv = item.get("servers")
                m = item.get("metrics", {})
                metric_tuples.append((
                    s_id, "2026-08-01",
                    l_rate, m_rate, serv,
                    m.get("utilization"), m.get("Lq"), m.get("Wq_hours"),
                    m.get("L"), m.get("W_hours"), m.get("p0"),
                    m.get("stable")
                ))
            execute_values(cur, """
                INSERT INTO queue_metrics (
                    shop_id, date, lambda_val, mu_val, servers_s, rho, lq, wq, l_val, w_val, p0, stable
                ) VALUES %s;
            """, metric_tuples)
        print("Populated queue_metrics table.")

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialization and population finished successfully!")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    populate_database(base_dir)

