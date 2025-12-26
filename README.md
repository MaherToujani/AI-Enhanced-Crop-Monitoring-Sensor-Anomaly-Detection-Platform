AI-Enhanced Crop Monitoring & Sensor Anomaly Detection Platform
An end-to-end platform for simulated agricultural sensor monitoring (soil moisture, temperature, humidity) with real-time anomaly detection and explainable recommendations. The system ingests sensor readings via a Django REST API, detects anomalies using a lightweight ML model (e.g., threshold / Isolation Forest), and generates human-readable actions via a rule-based AI agent.
​

Features
Django 5 backend with Django REST Framework (DRF) APIs for ingestion and retrieval.
​

Data model covering farms/plots, sensor readings, anomaly events, and recommendations.
​

Sensor simulation script generating realistic time-series patterns + injected anomalies (drops/spikes/drift).
​

ML anomaly detection module (threshold-based or Isolation Forest) triggered on new readings or in batches.
​

Rule-based AI agent producing explainable, template-driven recommendations (no LLM required).
​

Docker Compose setup for local end-to-end execution (Django + PostgreSQL; optional Redis).
​

Architecture
High-level flow:

Simulator sends readings (HTTP POST) to the Django API.
​

Backend persists readings in PostgreSQL.
​

ML module runs inference and creates an AnomalyEvent when needed.
​

AI agent generates an AgentRecommendation tied to the anomaly with an explanation and confidence.
​

Frontend dashboard consumes REST APIs to show charts, anomalies, and recommendations.
​

Tech Stack
Backend: Django 5 + Django REST Framework.
​

Auth: JWT + basic role-based permissions (e.g., admin/farmer).
​

DB: PostgreSQL (SQLite possible for dev).
​

ML/Simulation: Python + NumPy (+ scikit-learn if Isolation Forest is used).
​

Deployment: Docker + Docker Compose.
​

Frontend: (Your choice) React / Angular / Vue / Next.js / Django templates.
​

Data Model (Core Entities)
FarmProfile: owner, location, size, crop type.
​

FieldPlot: belongs to a farm, crop variety.
​

SensorReading: timestamp, plot, sensor type (moisture/temperature/humidity), value, source (simulator).
​

AnomalyEvent: timestamp, plot, anomaly type, severity, model confidence.
​

AgentRecommendation: timestamp, anomaly event, action, explanation text, confidence.
​

API Endpoints (Example)
Typical endpoints expected by the project scope:
​

POST /api/sensor-readings/ — ingest a new sensor reading.
​

GET /api/sensor-readings/?plotId=... — retrieve readings for a plot.
​

GET /api/anomalies/ — list anomaly events.
​

GET /api/recommendations/ — list agent recommendations.
​

If your actual routes differ, update this section to match your urls.py.

Local Setup (Without Docker)
1) Clone + create environment
bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
# .venv\Scripts\activate
2) Install dependencies
bash
pip install -r requirements.txt
3) Configure environment variables
Create a .env file (do not commit it). Use the same approach recommended by the project specs for secrets management.
​

Example:

text
DEBUG=1
SECRET_KEY=change-me
DATABASE_URL=postgres://user:password@localhost:5432/agri_db
JWT_SIGNING_KEY=change-me-too
4) Migrate + run
bash
python manage.py migrate
python manage.py runserver
Run with Docker Compose
This project is designed to run locally end-to-end using Docker Compose (Django + PostgreSQL).
​

bash
docker compose up --build
Then open:

Backend API: http://localhost:8000/

If your compose exposes different ports/services, update this section accordingly.

Sensor Simulator
A Python simulator generates realistic agricultural time-series (diurnal temperature cycle, moisture decay + irrigation-like increases, humidity correlation) and can inject anomalies (sudden drops, spikes, drift) for testing.
​

Example run (adjust to your script name):

bash
python simulator/run_simulator.py --base-url http://localhost:8000 --plot 1 --interval 10
ML Module
Supported approaches (choose at least one):
​

Threshold-based ranges (fast baseline, no training).
​

Isolation Forest (unsupervised outlier detection using scikit-learn).
​

Rolling statistics (moving mean/std + z-score style detection).
​

AI Agent (Explainable Recommendations)
The agent is a lightweight rule engine that converts detected anomalies into actionable advice with deterministic explanations (template-based).
​

Example rule patterns include:

Rapid moisture drop ⇒ check irrigation/leak/pump failure.
​

Sustained high temperature anomaly ⇒ heat stress mitigation (shade/irrigation frequency).
​

Multiple anomalies together ⇒ recommend full plot inspection.
​

Evaluation
This project supports basic evaluation metrics (precision, recall, F1-score) using synthetic data with known anomaly labels (ground truth).
​

Project Structure (Suggested)
text
.
├── backend/
│   ├── manage.py
│   ├── apps/
│   │   ├── core/               # Farm/Plot/Readings models
│   │   ├── ml_module/          # anomaly detection
│   │   └── agent/              # rule-based recommendations
├── simulator/
│   └── run_simulator.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
