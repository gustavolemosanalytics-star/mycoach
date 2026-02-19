import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import ProtectedRoute from './components/auth/ProtectedRoute'
import PlanScreen from './pages/PlanScreen'
import AddScreen from './pages/AddScreen'
import ProfileScreen from './pages/ProfileScreen'
import ActivityDetail from './pages/ActivityDetail'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<PlanScreen />} />
            <Route path="/add" element={<AddScreen />} />
            <Route path="/profile" element={<ProfileScreen />} />
            <Route path="/activity/:id" element={<ActivityDetail />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
