# 💈 PFI UADE - Sistema de Predicción de Ausentismo y Optimización de Capacidad

Sistema integral de gestión predictiva de ausentismo (*No-Show*) y optimización estocástica de capacidad operativa para comercios de servicios con agenda híbrida (Barberías / Centros de Estética / Servicios Personales).

Desarrollado como Proyecto de Fin de Ingeniería (PFI) - Universidad Argentina de la Empresa (UADE), 2026.

---

## 🛠️ Stack Tecnológico

- **Frontend:** React 19, Vite, TypeScript, Modern Grid CSS.
- **Backend:** FastAPI, Uvicorn (ASGI), Pydantic v2, Python 3.13.
- **Base de Datos & Persistencia:** PostgreSQL 15, Docker Compose, `psycopg2-binary`.
- **Motor Analítico & ML:** Pandas, NumPy, Scikit-learn, XGBoost, `hashlib` (SHA-256 + Salt).
- **Modelado Matemático:** Teoría de Colas Estocástica ($M/M/s$).

---

## 📁 Estructura del Proyecto

```text
pfi/
├── .env                         # Configuración de variables de entorno y Feature Flags
├── docker-compose.yml           # Orquestación de PostgreSQL y FastAPI Backend
├── requirements.txt             # Dependencias de Python backend y data pipeline
├── README.md                    # Documentación principal del repositorio
│
├── backend/                     # API Backend en FastAPI
│   ├── Dockerfile
│   └── app/
│       ├── main.py              # Punto de entrada de FastAPI y middlewares (CORS)
│       ├── config.py            # Carga de variables de entorno y rutas de almacenamiento
│       ├── routers/
│       │   ├── calendar.py      # REST Endpoint GET /api/calendar
│       │   └── queues.py        # REST Endpoint GET /api/queues
│       ├── schemas/             # DTOs y validación con Pydantic v2
│       │   ├── calendar.py
│       │   └── queues.py
│       └── services/
│           ├── db_service.py    # Consultas SQL para PostgreSQL
│           ├── calendar_service.py # Servicio de agenda con detección predictiva de riesgo
│           └── queue_service.py # Servicio de serving para teoría de colas M/M/s
│
├── data/                        # Almacenamiento de Datasets
│   ├── raw/                     # CSVs originales anonimizados (Hellfish y Hooligans)
│   │   ├── hellfish/            # appointments.csv, barbers.csv, services.csv
│   │   └── hooligans/           # appointments.csv, barbers.csv, services.csv
│   └── processed/               # Data matrizz procesada
│       ├── processed_appointments_matrix.csv
│       ├── consolidated_blocks.csv
│       └── queue_metrics.json
│
├── data_pipeline/               # Pipeline de Ingeniería de Datos y Simulación
│   ├── etl_pipeline.py          # Proceso ETL: limpieza, aislamiento de bloqueos y hashing SHA-256
│   ├── init_db.py               # Script de creación del esquema relacional e ingesta en PostgreSQL
│   ├── queuing_theory.py        # Cálculo estocástico de parámetros M/M/s (λ, μ, ρ, Lq, Wq)
│   └── utils.py                 # Auxiliares criptográficos y DateTime
│
└── frontend/                    # Dashboard Web en React 19 + TypeScript
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx              # Componente principal con navegación por pestañas y modo Fallback
        ├── components/          # Tarjetas M/M/s, Timeline de Agenda, Modales de Triggers
        └── data/
            └── fallbackData.ts  # Datos estáticos de resiliencia local
```

---

## ⚙️ Modos de Ejecución y Feature Flag (`DATA_SOURCE`)

El backend soporta un **Feature Flag de fuente de datos** mediante la variable de entorno `DATA_SOURCE` en el archivo `.env`:

1. **`DATA_SOURCE=POSTGRES` (Modo Recomendado / Producción):**
   - Consume los datos directamente de la base de datos relacional PostgreSQL activa en Docker.
   - Cuenta con **Mecanismo de Resiliencia (Fallback)**: Si la base de datos PostgreSQL no responde o cae, el backend conmuta automáticamente a leer los archivos CSV sin interrupción del servicio.

2. **`DATA_SOURCE=CSV` (Modo Liviano / Local):**
   - Consume directamente los datasets procesados en `data/processed/` sin requerir conexión a base de datos.

---

## 🚀 Guía de Instalación y Puesta en Marcha

### 1. Requisitos Previos
- Docker y Docker Desktop instalados y corriendo.
- Node.js (v18+) y `npm`.
- Python 3.11+.

### 2. Configurar Variables de Entorno
Asegurarse de que el archivo `.env` en la raíz del proyecto contenga:

```env
# Backend & CORS
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ALLOWED_ORIGINS=http://localhost:5173

# Feature Flag & Base de Datos PostgreSQL
DATA_SOURCE=POSTGRES
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pfi_db
DB_USER=postgres
DB_PASS=postgres

# Salts Criptográficos (Ley 25.326)
HELLFISH_SALT=HF_2026_SALT
HOOLIGANS_SALT=HL_2026_SALT
```

### 3. Encender la Infraestructura (PostgreSQL + FastAPI Backend)

```bash
# Desde la raíz del proyecto (pfi/)
docker compose up -d
```

### 4. Inicializar y Poblar la Base de Datos PostgreSQL

```bash
# Ejecutar el script de ingesta (crea las 5 tablas relacionales e inserta los 5.320 registros)
python3 data_pipeline/init_db.py
```

### 5. Iniciar el Dashboard Frontend (React + Vite)

```bash
# En una nueva terminal, acceder a la carpeta frontend
cd frontend
npm install
npm run dev
```

El dashboard estará disponible en: **`http://localhost:5173`**

---

## 🔌 Endpoints de la REST API (FastAPI)

Una vez iniciado el backend, se puede acceder a la documentación interactiva OpenAPI (Swagger UI) en:
👉 **`http://localhost:8000/docs`**

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/calendar?shop_id={hellfish\|hooligans}&date={YYYY-MM-DD}` | Devuelve la agenda del día con categorización predictiva de riesgo de ausentismo (`ALTO`, `MEDIO`, `BAJO`). |
| `GET` | `/api/queues` | Devuelve los parámetros estocásticos del modelo de colas $M/M/s$ ($\lambda, \mu, \rho, L_q, W_q, P_0$, estado de estabilidad) por comercio. |

---

## 🔒 Cumplimiento Normativo (Ley N° 25.326)

Toda la información personal e identificable de clientes (nombres y números telefónicos) es sometida a un proceso irreversibles de **anonimización criptográfica mediante algoritmos Hash SHA-256 combinados con sales dinámicas por comercio (*Salted Hashing*)** durante la fase ETL, garantizando el cumplimiento normativo de la Ley Argentina de Protección de Datos Personales.

---

## 🛑 Apagado del Sistema y Liberación de Recursos

### 1. Detener el Frontend (React)
En la terminal donde ejecutaste `npm run dev`, presioná:
```bash
Ctrl + C
```

### 2. Apagar los Contenedores Docker (PostgreSQL + Backend FastAPI)
Desde la raíz del proyecto (`pfi/`), ejecutá:
```bash
docker compose down
```

> 💡 **Nota:** Si en algún momento querés apagar los contenedores y **eliminar los volúmenes de datos temporales**, podés usar `docker compose down -v`.

---

## 📄 Licencia y Autores

- **Proyecto:** Proyecto de Fin de Ingeniería (PFI)
- **Institución:** Universidad Argentina de la Empresa (UADE) - 2026.

