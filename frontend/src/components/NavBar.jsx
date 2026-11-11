import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import RankBadge from './RankBadge'

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // "Guild Hall" stays lit while you're on any guild's quest board.
  const hallIsActive = ({ isActive }) =>
    isActive || window.location.pathname.startsWith('/guilds/') ? 'active' : undefined

  return (
    <header className="navbar">
      <Link to="/" className="brand">
        <span className="brand-mark" aria-hidden="true">⚔</span> The Guild
      </Link>
      {user && (
        <nav className="nav-links" aria-label="Main">
          <NavLink to="/" end className={hallIsActive}>Guild Hall</NavLink>
          <NavLink to="/profile">My License</NavLink>
          <span className="nav-xp">
            <RankBadge rank={user.rank} />
            {user.xp} XP
          </span>
          <button className="btn btn-ghost" onClick={handleLogout}>Leave the hall</button>
        </nav>
      )}
    </header>
  )
}
