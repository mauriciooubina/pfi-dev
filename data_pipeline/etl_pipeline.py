import os
import hashlib
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from data_pipeline.utils import (
        get_crypto_salt,
        hash_sensitive_data,
        safe_parse_datetime,
        make_tz_naive
    )
except ImportError:
    from utils import (
        get_crypto_salt,
        hash_sensitive_data,
        safe_parse_datetime,
        make_tz_naive
    )


def run_etl(raw_data_dir: str, processed_data_dir: str):
    """
    Executes the complete ETL pipeline for the real raw CSV files.
    """
    shops = ["hellfish", "hooligans"]
    all_processed_dfs = []
    all_blocks_dfs = []

    print(f"Starting ETL Pipeline on REAL dataset. Raw directory: {raw_data_dir}")

    for shop in shops:
        shop_raw_dir = os.path.join(raw_data_dir, shop)
        appointments_path = os.path.join(shop_raw_dir, "appointments.csv")
        barbers_path = os.path.join(shop_raw_dir, "barbers.csv")
        services_path = os.path.join(shop_raw_dir, "services.csv")

        # Check if files exist
        if not (os.path.exists(appointments_path) and os.path.exists(barbers_path) and os.path.exists(services_path)):
            print(f"[Warning] Missing raw files for shop '{shop}' in '{shop_raw_dir}'. Skipping.")
            continue

        print(f"\nProcessing shop: {shop}")
        
        # Load datasets
        df_app = pd.read_csv(appointments_path)
        df_barbers = pd.read_csv(barbers_path)
        df_services = pd.read_csv(services_path)

        print(f"Loaded {len(df_app)} appointments, {len(df_barbers)} barbers, {len(df_services)} services.")

        # Ensure correct datatypes and clean whitespace
        df_app['phone'] = df_app['phone'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
        df_app['client'] = df_app['client'].astype(str).str.strip()
        df_app['created_by'] = df_app['created_by'].astype(str).str.strip()
        df_app['deleted_by'] = df_app['deleted_by'].astype(str).str.strip()

        # Add shop identifier
        df_app['shop_id'] = shop

        # --- A. Isolation of Calendar Blocks (Filtro Core) ---
        # Condition: phone == "0000000000" or client contains control variables
        control_keywords = ["ALMUERZO", "HORARIO", "BLOQUEO"]
        is_block_phone = df_app['phone'] == "0000000000"
        
        pattern = "|".join(control_keywords)
        is_block_client = df_app['client'].str.contains(pattern, case=False, na=False)
        
        is_block = is_block_phone | is_block_client

        # Split technical calendar blocks from real patient appointments
        df_blocks = df_app[is_block].copy()
        df_clients = df_app[~is_block].copy()
        
        print(f"Isolated {len(df_blocks)} calendar blocks. {len(df_clients)} client appointments remaining.")

        # Save blocks to list for analytical idleness calculations later
        all_blocks_dfs.append(df_blocks)

        if df_clients.empty:
            print(f"No client appointments to process for {shop}.")
            continue

        # --- B. Feature Engineering ---
        # 1. is_self_booked
        # Handle NaN values safely by filling or checking equality
        df_clients['is_self_booked'] = (
            (df_clients['created_by'].notna()) & 
            (df_clients['client'].notna()) & 
            (df_clients['created_by'] == df_clients['client'])
        ).astype(int)

        # 2. DateTime features
        appointment_start = make_tz_naive(safe_parse_datetime(df_clients['date'], df_clients['start_time']))
        df_clients['appointment_start'] = appointment_start
        df_clients['day_of_week'] = appointment_start.dt.dayofweek
        df_clients['hour_of_day'] = appointment_start.dt.hour
        df_clients['month'] = appointment_start.dt.month

        # 3. Reaction times
        created_at_dt = make_tz_naive(safe_parse_datetime(df_clients['created_at']))
        deleted_at_dt = make_tz_naive(safe_parse_datetime(df_clients['deleted_at']))
        
        # Calculate margins safely
        df_clients['lead_time_hours'] = (appointment_start - created_at_dt).dt.total_seconds() / 3600.0
        df_clients['cancelation_margin_hours'] = (appointment_start - deleted_at_dt).dt.total_seconds() / 3600.0

        # --- C. Target Labeling (Rule-based) ---
        paid_bool = df_clients['paid'].astype(str).str.lower().isin(['true', '1', '1.0', 't', 'y', 'yes'])
        is_deleted = df_clients['deleted_at'].notna() & (df_clients['deleted_at'].astype(str).str.strip().str.lower() != 'nan')

        # Define targets
        # Condition 1: Asistencia (y = 0): deleted_at is NULL and paid is True
        cond_asistencia = (~is_deleted) & paid_bool

        # Condition 2: No-Show Absoluto (y = 1): deleted_at is NULL and paid is False
        cond_noshow_abs = (~is_deleted) & (~paid_bool)

        # Condition 3: No-Show Proxy por Eliminación del Local (y = 1): deleted_at is NOT NULL, but deleted_by != client
        cond_noshow_elim = is_deleted & (df_clients['deleted_by'] != df_clients['client'])

        # Condition 4: No-Show Proxy por Cancelación Tardía (y = 1): deleted_at is NOT NULL, deleted_by == client, but cancelation_margin_hours < 2.0
        cond_noshow_late = is_deleted & (df_clients['deleted_by'] == df_clients['client']) & (df_clients['cancelation_margin_hours'] < 2.0)

        # Condition 5: Cancelación Anticipada Legítima (Exclusión de Target): deleted_at is NOT NULL, deleted_by == client, and cancelation_margin_hours >= 2.0
        cond_exclusion = is_deleted & (df_clients['deleted_by'] == df_clients['client']) & (df_clients['cancelation_margin_hours'] >= 2.0)

        # Assign targets
        df_clients['target'] = np.nan
        df_clients.loc[cond_asistencia, 'target'] = 0
        df_clients.loc[cond_noshow_abs, 'target'] = 1
        df_clients.loc[cond_noshow_elim, 'target'] = 1
        df_clients.loc[cond_noshow_late, 'target'] = 1

        print(f"Target distribution before exclusion:\n{df_clients['target'].value_counts(dropna=False)}")

        # Exclude legitimate early cancellations from the ML matrix
        df_ml = df_clients[~cond_exclusion].copy()
        
        # Drop rows where target could not be calculated (should not be training items)
        df_ml = df_ml.dropna(subset=['target'])
        df_ml['target'] = df_ml['target'].astype(int)

        print(f"After early cancellation exclusion, training records for ML: {len(df_ml)}")

        # --- D. Cryptographic Anonymization (Ley 25.326) ---
        salt = get_crypto_salt(shop)
        df_ml['client_hashed'] = df_ml['client'].apply(lambda x: hash_sensitive_data(x, salt))
        df_ml['phone_hashed'] = df_ml['phone'].apply(lambda x: hash_sensitive_data(x, salt))
        
        # Drop raw identity columns
        df_ml = df_ml.drop(columns=['client', 'phone'])

        # --- E. Merge with Barbers & Services metadata ---
        df_services_renamed = df_services.rename(columns={
            'id': 'service_id', 
            'name': 'service_name',
            'price': 'service_price',
            'image': 'service_image'
        })
        df_ml = df_ml.merge(df_services_renamed, on='service_id', how='left')

        df_barbers_renamed = df_barbers.rename(columns={
            'id': 'barber_id',
            'name': 'barber_name',
            'role': 'barber_role',
            'active': 'barber_active'
        })
        df_ml = df_ml.merge(df_barbers_renamed[['barber_id', 'barber_name', 'barber_role', 'barber_active']], on='barber_id', how='left')

        all_processed_dfs.append(df_ml)

    # --- Save Outputs ---
    if not os.path.exists(processed_data_dir):
        os.makedirs(processed_data_dir, exist_ok=True)

    if all_processed_dfs:
        consolidated_df = pd.concat(all_processed_dfs, ignore_index=True)
        matrix_path = os.path.join(processed_data_dir, "processed_appointments_matrix.csv")
        consolidated_df.to_csv(matrix_path, index=False)
        print(f"\nETL Success! Processed appointments matrix saved to: {matrix_path} (Total: {len(consolidated_df)} rows)")
    else:
        print("\n[Error] No appointments were successfully processed from raw files.")

    if all_blocks_dfs:
        consolidated_blocks = pd.concat(all_blocks_dfs, ignore_index=True)
        blocks_path = os.path.join(processed_data_dir, "consolidated_blocks.csv")
        consolidated_blocks.to_csv(blocks_path, index=False)
        print(f"Saved {len(consolidated_blocks)} isolated calendar blocks to: {blocks_path}")


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    run_etl(raw_dir, processed_dir)
