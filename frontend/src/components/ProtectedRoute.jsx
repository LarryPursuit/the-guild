import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Loading from './Loading'

// Wraps pages that need a logged-in user; sends everyone else to /login.
export default function ProtectedRoute() {
  const { user, checking } = useAuth()
  if (checking) return <Loading label="Checking your guild papers…" />
  return user ? <Outlet /> : <Navigate to="/login" replace />
}
