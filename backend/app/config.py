import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173").split(",")
DATA_SOURCE = os.getenv("DATA_SOURCE", "POSTGRES").upper()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "pfi_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")

PROCESSED_FILE = os.path.join(BASE_DIR, "data", "processed", "processed_appointments_matrix.csv")
QUEUE_METRICS_JSON = os.path.join(BASE_DIR, "data", "processed", "queue_metrics.json")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")

BARBERS_CSV = {
    "hellfish": os.path.join(RAW_DIR, "hellfish", "barbers.csv"),
    "hooligans": os.path.join(RAW_DIR, "hooligans", "barbers.csv")
}
SERVICES_CSV = {
    "hellfish": os.path.join(RAW_DIR, "hellfish", "services.csv"),
    "hooligans": os.path.join(RAW_DIR, "hooligans", "services.csv")
}
