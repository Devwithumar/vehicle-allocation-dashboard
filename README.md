# vehicle-allocation-dashboard
A production-ready Python dashboard for fleet management, featuring vehicle allocation visualizations, Gantt and bar charts, conflict detection, Excel import, and a FastAPI backend skeleton for optional GPS tracking.
# 🚛 Vehicle Allocation Dashboard

[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.22-orange)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Issues](https://img.shields.io/github/issues/<your-username>/<your-repo>)](https://github.com/<your-username>/<your-repo>/issues)
vehicle-allocation-dashboard/

## Quick Start (Local)

1. **Clone the repo**
```bash
git clone <your-repo-url>
cd vehicle-allocation-dashboard

2. **create a virtual environment**
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

3. **Install depencies
pip install -r requirements.txt

4. **Run on streamlit server**
" streamlit run app.py" in terminal

5.** pip install fastapi[all] uvicorn**
uvicorn backend.main:app --reload --port 8000


6.**pip install fastapi[all] uvicorn
uvicorn backend.main:app --reload --port 8000


---

## Features

### Streamlit Dashboard
- Upload Excel (.xlsx/.xls) with intelligent column mapping
- **Interactive Visualizations**:
  - Gantt Timeline (weekly view)
  - Vehicle Utilization (total hours per vehicle)
  - Daily Allocation Overview
- Quick Insights Cards with key metrics
- Conflict Detection (scheduling overlaps)
- Filters by vehicle, day, journey type
- Responsive layout for desktop and mobile
- Premium color themes: **Green, Beige, Grey, Cobalt Blue**
- Sample Excel template included (`samples/sample_data.xlsx`)
- Mini user profile: greet logged-in users by name (future OTP/email login)

### Backend (FastAPI Skeleton)
- Endpoints to receive vehicle GPS pings
- Fetch vehicle tracks
- Demo in-memory store (replace with DB in production)
- Health check endpoint
- Ready for expansion: OTP login, DB models, authentication

### Advanced Features
- Flexible data import: header detection, auto column mapping
- Data validation and error handling
- Hover details and interactive filtering
- Routine schedules for drivers
- Vehicle tracking with optional Google Maps integration

---

## Project Structure
├── app.py
├── utils.py
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── Procfile
├── samples/
│ └── sample_data.xlsx
├── backend/
│ ├── main.py
│ ├── models.py
│ └── README.md
└── tests/
└── test_utils.py

##soon to add


OTP email login

Real-time GPS tracking

Database integration

Enhanced analytics

Deployment scripts / Docker
