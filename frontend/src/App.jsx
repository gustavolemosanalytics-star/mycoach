import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Wellness from './pages/Wellness';
import Achievements from './pages/Achievements';
import WorkoutDetail from './pages/WorkoutDetail';
import Workouts from './pages/Workouts';
import Analytics from './pages/Analytics';
import Nutrition from './pages/Nutrition';

function Integrations() {
  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Integrações</h1>
        <p className="page-subtitle">Conecte seu Strava e Garmin</p>
      </header>
      <div className="card">
        <p>Página de integrações em desenvolvimento...</p>
      </div>
    </div>
  );
}

function Settings() {
  return (
    <div>
      <header className="page-header">
        <h1 className="page-title">Configurações</h1>
        <p className="page-subtitle">Personalize sua experiência</p>
      </header>
      <div className="card">
        <p>Página de configurações em desenvolvimento...</p>
      </div>
    </div>
  );
}

function PublicRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return isAuthenticated ? <Navigate to="/" replace /> : children;
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          <Route path="/register" element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          } />

          {/* Protected routes */}
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/workouts" element={<Workouts />} />
            <Route path="/wellness" element={<Wellness />} />
            <Route path="/achievements" element={<Achievements />} />
            <Route path="/workouts/:id" element={<WorkoutDetail />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/integrations" element={<Integrations />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/nutrition" element={<Nutrition />} />
            <Route path="/nutrition/anamnesis" element={<Anamnesis />} />
            <Route path="/nutrition/chat" element={<NutritionChat />} />
          </Route>

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
