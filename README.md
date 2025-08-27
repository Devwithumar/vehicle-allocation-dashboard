# Vehicle Allocation Dashboard

Streamlit dashboard + FastAPI skeleton for managing and visualizing vehicle allocation schedules.
This repo is a ready-to-upload GitHub project demonstrating the core functionality described in the design brief:
- Excel upload (.xlsx/.xls) with intelligent column mapping
- Gantt timeline and utilization charts
- Conflict detection and quick analytics
- Theme selector with four polished themes
- FastAPI backend skeleton for GPS tracking (demo)

## Quick start (local)

```bash
git clone <this-repo>
cd vehicle-allocation-dashboard
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
# run streamlit app
streamlit run app.py
# (optional) run backend demo server
# pip install fastapi[all] uvicorn
# uvicorn backend.main:app --reload --port 8000
```

## Notes
- Add API keys (SendGrid, Google Maps) to `.env` and configure before using those optional features.
- This repo includes a sample Excel template in `samples/sample_data.xlsx`.
- For production, replace in-memory demo stores with a proper DB (Postgres) and secure the endpoints.
