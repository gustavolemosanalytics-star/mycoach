# Backend - MyCoach API

FastAPI backend for MyCoach platform.

## Setup Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor de desenvolvimento
uvicorn app.main:app --reload --port 8000
```

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/mycoach
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Strava API
STRAVA_CLIENT_ID=your-client-id
STRAVA_CLIENT_SECRET=your-client-secret
STRAVA_REDIRECT_URI=http://localhost:8000/api/integrations/strava/callback

# Garmin API (optional)
GARMIN_CLIENT_ID=your-client-id
GARMIN_CLIENT_SECRET=your-client-secret
```

## Deploy to Railway

This project is configured for Railway deployment. Just connect your GitHub repo and Railway will auto-detect the configuration.
