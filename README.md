# MyCoach - Plataforma de Coaching para Triatletas e Maratonistas

Monorepo contendo backend (Python/FastAPI) e frontend (React/Vite) para plataforma de coaching esportivo.

## Estrutura do Projeto

```
mycoach/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── models/    # SQLAlchemy models
│   │   ├── routers/   # API endpoints
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── utils/     # Helpers
│   └── requirements.txt
│
└── frontend/          # React SPA
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── context/
    │   └── services/
    └── package.json
```

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database URL and secrets
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Deploy to Railway

1. Create a new Railway project
2. Add a PostgreSQL database
3. Connect your GitHub repository
4. Add two services: `backend` and `frontend`
5. Set environment variables:

**Backend:**
- `DATABASE_URL` (from Railway PostgreSQL)
- `JWT_SECRET_KEY` (generate a random string)
- `FRONTEND_URL` (your frontend Railway URL)
- `STRAVA_CLIENT_ID` (optional)
- `STRAVA_CLIENT_SECRET` (optional)

**Frontend:**
- `VITE_API_URL` (your backend Railway URL + /api)

## Features

- 🏃 **Workouts**: Sync from Strava/Garmin, manual entry, detailed analytics
- 🧘 **Wellness**: Daily mood, sleep, stress, and readiness tracking
- 🏆 **Gamification**: Achievements, points, levels
- 📊 **Analytics**: Training load, trends, insights
- 🔗 **Integrations**: Strava OAuth (Garmin coming soon)
