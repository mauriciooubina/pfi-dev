import os
import csv
import random
from datetime import datetime, timedelta

def create_mock_data(base_dir: str):
    """
    Generates synthetic dataset of 5,175 total appointments across Hellfish and Hooligans
    following the specific business constraints, schemas, and rules.
    """
    raw_dir = os.path.join(base_dir, "data", "raw")
    os.makedirs(os.path.join(raw_dir, "hellfish"), exist_ok=True)
    os.makedirs(os.path.join(raw_dir, "hooligans"), exist_ok=True)

    # 1. Barbers
    # Hellfish: Facundo [ID 1, admin], Martin [ID 2, barber], Alan [ID 3, active:false], Mauro [ID 5, active:false], Mauro [ID 6, active:true]
    hellfish_barbers = [
        {"id": 1, "name": "Facundo", "role": "admin", "image": "facundo.png", "email": "facundo@hellfish.com", "instagram": "facu_hellfish", "active": "True", "commission": 0.5, "sale_commission": 0.1},
        {"id": 2, "name": "Martín", "role": "barber", "image": "martin.png", "email": "martin@hellfish.com", "instagram": "martin_barber", "active": "True", "commission": 0.4, "sale_commission": 0.1},
        {"id": 3, "name": "Alan", "role": "barber", "image": "alan.png", "email": "alan@hellfish.com", "instagram": "alan_inactive", "active": "False", "commission": 0.4, "sale_commission": 0.1},
        {"id": 5, "name": "Mauro Inactivo", "role": "barber", "image": "mauro5.png", "email": "mauro5@hellfish.com", "instagram": "mauro_inactive", "active": "False", "commission": 0.4, "sale_commission": 0.1},
        {"id": 6, "name": "Mauro", "role": "barber", "image": "mauro6.png", "email": "mauro@hellfish.com", "instagram": "mauro_active", "active": "True", "commission": 0.4, "sale_commission": 0.1}
    ]

    # Hooligans: Sebastian Fraga [ID 1, admin], Valen [ID 4, active:false], Valentino [ID 5, active:true]
    hooligans_barbers = [
        {"id": 1, "name": "Sebastián Fraga", "role": "admin", "image": "seba.png", "email": "seba@hooligans.com", "instagram": "seba_hooli", "active": "True", "commission": 0.5, "sale_commission": 0.1},
        {"id": 4, "name": "Valen", "role": "barber", "image": "valen.png", "email": "valen@hooligans.com", "instagram": "valen_inactive", "active": "False", "commission": 0.4, "sale_commission": 0.1},
        {"id": 5, "name": "Valentino", "role": "barber", "image": "valentino.png", "email": "valentino@hooligans.com", "instagram": "vale_active", "active": "True", "commission": 0.4, "sale_commission": 0.1}
    ]

    # Save barbers
    for shop, data in [("hellfish", hellfish_barbers), ("hooligans", hooligans_barbers)]:
        path = os.path.join(raw_dir, shop, "barbers.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    # 2. Services
    services_data = [
        {"id": 1, "name": "Corte Clásico", "description": "Corte a tijera o máquina tradicional", "price": 4500, "image": "corte.png", "duration": 30},
        {"id": 2, "name": "Corte y Barba", "description": "Corte de cabello y perfilado de barba", "price": 6000, "image": "combo.png", "duration": 45},
        {"id": 3, "name": "Perfilado de Barba", "description": "Arreglo y perfilado con navaja", "price": 2500, "image": "barba.png", "duration": 20},
        {"id": 4, "name": "Color y Fade", "description": "Color de fantasía o decoloración con corte", "price": 12000, "image": "color.png", "duration": 90}
    ]

    for shop in ["hellfish", "hooligans"]:
        path = os.path.join(raw_dir, shop, "services.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=services_data[0].keys())
            writer.writeheader()
            writer.writerows(services_data)

    # 3. Appointments
    # We need 5175 total rows consolidated. Let's make:
    # Hellfish: 3100 appointments
    # Hooligans: 2075 appointments
    start_date = datetime(2026, 1, 1)
    
    clients = ["Juan Perez", "Carlos Gomez", "Matias Lopez", "Lucas Rodriguez", "Nicolas Diaz", "Agustin Silva"]
    phones = ["1144558899", "1122334455", "1166778899", "1155443322", "1133221100", "1199887766"]
    
    # Mappings
    barbers_by_shop = {
        "hellfish": [1, 2, 3, 5, 6], # includes active and inactive
        "hooligans": [1, 4, 5]
    }

    fieldnames = [
        "id", "barber_id", "date", "start_time", "client", "phone", "paid",
        "price", "end_time", "service_id", "created_at", "created_by",
        "deleted_at", "deleted_by", "updated_at"
    ]

    for shop, target_count in [("hellfish", 3100), ("hooligans", 2075)]:
        barber_ids = barbers_by_shop[shop]
        appointments = []
        
        for app_id in range(1, target_count + 1):
            # Pick a date/time
            day_offset = random.randint(0, 150) # Jan to May 2026
            app_date = start_date + timedelta(days=day_offset)
            
            # Operating hours: 10:00 to 20:00. Start times every 30 mins
            hour = random.randint(10, 19)
            minute = random.choice([0, 30])
            start_time = f"{hour:02d}:{minute:02d}:00"
            
            service = random.choice(services_data)
            duration_minutes = service["duration"]
            
            # End time
            end_dt = datetime.strptime(start_time, "%H:%M:%S") + timedelta(minutes=duration_minutes)
            end_time = end_dt.strftime("%H:%M:%S")
            
            barber_id = random.choice(barber_ids)
            
            # Select scenario type to test ETL labeling
            scenario = random.choices(
                ["show", "no_show_abs", "block", "late_cancel", "early_cancel", "shop_deleted"],
                weights=[70, 10, 5, 5, 5, 5],
                k=1
            )[0]
            
            client = random.choice(clients)
            phone = random.choice(phones)
            paid = "True"
            created_by = client if random.random() > 0.3 else "admin"
            deleted_at = ""
            deleted_by = ""
            
            app_start_dt = datetime.combine(app_date.date(), datetime.strptime(start_time, "%H:%M:%S").time())
            
            # created_at is a few hours to days before
            lead_time_days = random.randint(0, 5)
            lead_time_hours = random.randint(1, 23)
            created_at_dt = app_start_dt - timedelta(days=lead_time_days, hours=lead_time_hours)
            created_at = created_at_dt.strftime("%Y-%m-%d %H:%M:%S")
            
            if scenario == "block":
                if random.random() > 0.5:
                    phone = "0000000000"
                    client = random.choice(["BLOQUEO", "ALMUERZO", "HORARIO"])
                else:
                    phone = random.choice(phones)
                    client = random.choice(["ALMUERZO PERSONAL", "BLOQUEO TURNO", "HORARIO MEDICO"])
                paid = "False"
            elif scenario == "no_show_abs":
                paid = "False"
            elif scenario == "late_cancel":
                # client deleted, cancellation margin < 2 hours
                cancel_margin_minutes = random.randint(10, 110)
                deleted_at_dt = app_start_dt - timedelta(minutes=cancel_margin_minutes)
                deleted_at = deleted_at_dt.strftime("%Y-%m-%d %H:%M:%S")
                deleted_by = client
                paid = "False"
            elif scenario == "early_cancel":
                # client deleted, cancellation margin >= 2 hours (e.g. 5 hours)
                cancel_margin_hours = random.randint(2, 48)
                deleted_at_dt = app_start_dt - timedelta(hours=cancel_margin_hours)
                deleted_at = deleted_at_dt.strftime("%Y-%m-%d %H:%M:%S")
                deleted_by = client
                paid = "False"
            elif scenario == "shop_deleted":
                # deleted_by != client
                cancel_margin_hours = random.randint(1, 24)
                deleted_at_dt = app_start_dt - timedelta(hours=cancel_margin_hours)
                deleted_at = deleted_at_dt.strftime("%Y-%m-%d %H:%M:%S")
                deleted_by = "admin"
                paid = "False"
            
            appointments.append({
                "id": app_id,
                "barber_id": barber_id,
                "date": app_date.strftime("%Y-%m-%d"),
                "start_time": start_time,
                "client": client,
                "phone": phone,
                "paid": paid,
                "price": service["price"],
                "end_time": end_time,
                "service_id": service["id"],
                "created_at": created_at,
                "created_by": created_by,
                "deleted_at": deleted_at,
                "deleted_by": deleted_by,
                "updated_at": app_start_dt.strftime("%Y-%m-%d %H:%M:%S")
            })
            
        path = os.path.join(raw_dir, shop, "appointments.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(appointments)
            
    print(f"Mock data created successfully in {raw_dir}!")

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    create_mock_data(base_dir)
