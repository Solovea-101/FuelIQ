# FuelIQ Backend

FastAPI backend for FuelIQ fleet fuel management with ML-powered fuel consumption predictions.

## Quick Start

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install bcrypt==4.0.1  # compatibility fix

# Run migrations
alembic upgrade head

# Seed development data
python -m app.seed.seed_data

# Start server
uvicorn app.main:app --reload --port 8000
```

## ML Pipeline

```bash
# 1. Generate synthetic training data
python ml/scripts/generate_synthetic_data.py

# 2. Train model
python ml/scripts/train_model.py

# 3. Notebooks (optional)
jupyter notebook ml/notebooks/
```

## Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Driver | driver@fueliq.ke | driver123 |
| Manager | manager@fueliq.ke | manager123 |
| Admin | admin@fueliq.ke | admin123 |

## API Endpoints

All endpoints under `/api/v1`:

- **Auth**: `/auth/login`, `/auth/register`, `/auth/refresh`, `/auth/logout`, `/auth/me`
- **Trips**: `/trips`, `/trips/{id}`, `/trips/active`, `/trips/{id}/end`, `/trips/{id}/waypoints`
- **Vehicles**: `/vehicles`, `/vehicles/{id}`, `/vehicles/{id}/assign`
- **Drivers**: `/drivers`, `/drivers/performance`
- **Analytics**: `/analytics/fuel-efficiency`, `/analytics/daily`, `/analytics/summary`
- **Recommendations**: `/recommendations`
- **Budgets**: `/budgets`
- **Predictions**: `/predict/fuel-consumption`
- **Admin**: `/admin/users`, `/admin/analytics`, `/admin/settings`

Interactive docs: http://localhost:8000/docs
