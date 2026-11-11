import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import NavBar from './components/NavBar'
import ProtectedRoute from './components/ProtectedRoute'
import AuthPage from './pages/AuthPage'
import GuildHall from './pages/GuildHall'
import GuildPage from './pages/GuildPage'
import AdventurerProfile from './pages/AdventurerProfile'
import NotFound from './pages/NotFound'
import { useAuth } from './context/AuthContext'

export default function App() {
  const { user } = useAuth()
  const { pathname } = useLocation()

  // The front desk (login) is a full-bleed dark page; everything else sits in the centered container.
  if (pathname === '/login') {
    return user ? <Navigate to="/" replace /> : <AuthPage />
  }

  return (
    <>
      <NavBar />
      <main className="container">
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<GuildHall />} />
            <Route path="/guilds/:guildId" element={<GuildPage />} />
            <Route path="/profile" element={<AdventurerProfile />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
    </>
  )
}
