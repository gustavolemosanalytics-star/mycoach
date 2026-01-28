# Frontend - MyCoach

React frontend for MyCoach platform.

## Setup Local

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
```

## Deploy to Railway

This project is configured for Railway. Connect your GitHub repo and set the `VITE_API_URL` environment variable to your backend URL.

## Build for Production

```bash
npm run build
npm run preview
```
