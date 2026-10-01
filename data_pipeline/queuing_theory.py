import os
import json
import math
import pandas as pd
import numpy as np

def calculate_mms_metrics(lambda_rate: float, mu_rate: float, s: int):
    """
    Calculates standard M/M/s queuing model parameters.
    """
    if s <= 0 or mu_rate <= 0:
        return {
            "utilization": 0.0, "p0": 1.0, "Lq": 0.0,
            "Wq_hours": 0.0, "Wq_minutes": 0.0, "L": 0.0,
            "W_hours": 0.0, "W_minutes": 0.0, "stable": False
        }

    rho = lambda_rate / (s * mu_rate)
    
    if rho >= 1.0:
        return {
            "utilization": rho,
            "p0": 0.0,
            "Lq": float('inf'),
            "Wq_hours": float('inf'),
            "Wq_minutes": float('inf'),
            "L": float('inf'),
            "W_hours": float('inf'),
            "W_minutes": float('inf'),
            "stable": False
        }

    sum_terms = 0.0
    for n in range(s):
        sum_terms += ((s * rho) ** n) / math.factorial(n)
        
    p0_inv = sum_terms + ((s * rho) ** s) / (math.factorial(s) * (1 - rho))
    p0 = 1.0 / p0_inv if p0_inv != 0 else 0.0

    lq_numerator = p0 * ((s * rho) ** s) * rho
    lq_denominator = math.factorial(s) * ((1 - rho) ** 2)
    Lq = lq_numerator / lq_denominator if lq_denominator != 0 else 0.0

    Wq_hours = Lq / lambda_rate if lambda_rate > 0 else 0.0
    Wq_minutes = Wq_hours * 60.0

    L = Lq + (lambda_rate / mu_rate)

    W_hours = L / lambda_rate if lambda_rate > 0 else (1.0 / mu_rate)
    W_minutes = W_hours * 60.0

    return {
        "utilization": float(rho),
        "p0": float(p0),
        "Lq": float(Lq),
        "Wq_hours": float(Wq_hours),
        "Wq_minutes": float(Wq_minutes),
        "L": float(L),
        "W_hours": float(W_hours),
        "W_minutes": float(W_minutes),
        "stable": True
    }


def analyze_queues(processed_appointments_path: str, barbers_path_dict: dict, services_path_dict: dict, output_json_path: str = None):
    """
    Computes λ, μ and M/M/s metrics for both Hellfish and Hooligans from processed data,
    saving the results to a JSON file.
    """
    if not os.path.exists(processed_appointments_path):
        print(f"[Error] Processed appointments file not found at {processed_appointments_path}")
        return {}

    df_all = pd.read_csv(processed_appointments_path)
    
    # Active barber ID lists
    active_barbers = {
        "hellfish": [1, 2, 6],
        "hooligans": [1, 5]
    }
    
    results_list = []
    results_dict = {}

    for shop in ["hellfish", "hooligans"]:
        print(f"\nQueue Analysis for: {shop}")
        
        df_shop = df_all[df_all['shop_id'] == shop].copy()
        if df_shop.empty:
            print(f"[Warning] No processed data found for {shop}.")
            continue

        barbers_csv = barbers_path_dict.get(shop)
        services_csv = services_path_dict.get(shop)

        if not barbers_csv or not os.path.exists(barbers_csv):
            print(f"[Warning] Barbers CSV not found for {shop}.")
            continue
        if not services_csv or not os.path.exists(services_csv):
            print(f"[Warning] Services CSV not found for {shop}.")
            continue

        df_services = pd.read_csv(services_csv)

        # 1. Active Servers (s)
        s_servers = len(active_barbers[shop])
        print(f"Active servers (s): {s_servers}")

        # 2. Arrival Rate (λ)
        # Parse times and filter between 10:00 and 20:00
        df_shop['start_hour'] = pd.to_datetime(df_shop['start_time'], format='%H:%M:%S', errors='coerce').dt.hour
        df_operational = df_shop[(df_shop['start_hour'] >= 10) & (df_shop['start_hour'] < 20)].copy()
        
        unique_days = df_operational['date'].nunique()
        if unique_days == 0:
            unique_days = df_shop['date'].nunique()
            
        total_operational_hours = unique_days * 10.0 # 10 hours (10:00 to 20:00)
        total_arrivals = len(df_operational)
        
        lambda_rate = total_arrivals / total_operational_hours if total_operational_hours > 0 else 0.0
        print(f"Operational window arrivals: {total_arrivals} over {unique_days} days ({total_operational_hours} hours)")
        print(f"Arrival Rate (λ): {lambda_rate:.4f} customers/hour")

        # 3. Service Rate (μ)
        # Only use served/non-cancelled appointments (target == 0) to get duration
        df_served = df_shop[df_shop['target'] == 0].copy()
        if df_served.empty:
            df_served = df_shop.copy()
            
        if 'duration' not in df_served.columns:
            df_served = df_served.merge(df_services[['id', 'duration']], left_on='service_id', right_on='id', how='left')
        
        mean_duration_minutes = df_served['duration'].mean()
        if pd.isna(mean_duration_minutes) or mean_duration_minutes <= 0:
            mean_duration_minutes = 30.0

        # μ = 60 / mean_duration
        mu_rate = 60.0 / mean_duration_minutes
        print(f"Average Duration: {mean_duration_minutes:.2f} minutes")
        print(f"Service Rate (μ) per server: {mu_rate:.4f} services/hour")

        # Calculate M/M/s metrics
        metrics = calculate_mms_metrics(lambda_rate, mu_rate, s_servers)
        
        # Structure matching API response schema
        shop_data = {
            "shop_id": shop,
            "lambda_rate": float(lambda_rate),
            "mu_rate": float(mu_rate),
            "servers": int(s_servers),
            "metrics": metrics
        }
        
        results_list.append(shop_data)
        results_dict[shop] = shop_data

    # Save to JSON file if specified
    if output_json_path:
        out_dir = os.path.dirname(output_json_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
            
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(results_list, f, indent=2, ensure_ascii=False)
        print(f"\nSaved dynamic queue metrics to JSON: {output_json_path}")

    return results_dict


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    processed_path = os.path.join(base_dir, "data", "processed", "processed_appointments_matrix.csv")
    json_path = os.path.join(base_dir, "data", "processed", "queue_metrics.json")
    
    barbers_dict = {
        "hellfish": os.path.join(base_dir, "data", "raw", "hellfish", "barbers.csv"),
        "hooligans": os.path.join(base_dir, "data", "raw", "hooligans", "barbers.csv")
    }
    
    services_dict = {
        "hellfish": os.path.join(base_dir, "data", "raw", "hellfish", "services.csv"),
        "hooligans": os.path.join(base_dir, "data", "raw", "hooligans", "services.csv")
    }
    
    analyze_queues(processed_path, barbers_dict, services_dict, json_path)
