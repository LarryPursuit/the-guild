import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import ErrorMessage from '../components/ErrorMessage'
import Notice from '../components/Notice'
import RankBadge from '../components/RankBadge'

const RANKS = ['Copper', 'Silver', 'Gold', 'Mythril']

export default function AuthPage() {
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const isRegister = mode === 'register'
  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (isRegister && form.password.length < 8) {
      setError('Your secret word must be at least 8 characters.')
      return
    }
    setSubmitting(true)
    try {
      if (isRegister) await register(form)
      else await login(form.username, form.password)
      navigate(isRegister ? '/profile' : '/')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="front-desk">
      <div className="front-desk-intro">
        <p className="eyebrow"><span aria-hidden="true">⚔</span> The Adventurers&apos; Guild</p>
        <h1>Every task is a quest. Every quest pays.</h1>
        <p className="lead">
          Pin your goals to the board, clear requests for XP, and climb from Copper to Mythril. Each cleared quest
          drops a piece of real D&amp;D 5e loot into your pack.
        </p>
        <ul className="rank-ladder" aria-label="Guild ranks">
          {RANKS.map((rank) => (
            <li key={rank}><RankBadge rank={rank} /></li>
          ))}
        </ul>
      </div>

      <div className="corkboard front-desk-board">
        <Notice as="form" className="front-desk-notice" pin="pin-red" pinSize="pin-large" onSubmit={handleSubmit}>
          <p className="eyebrow">Notice of the front desk</p>
          <h2>{isRegister ? 'Guild Registration' : 'Return to the Guild'}</h2>
          <ErrorMessage message={error} onDismiss={() => setError('')} />
          <label className="field">
            Adventurer name
            <input value={form.username} onChange={update('username')} autoComplete="username" placeholder="Mira" required />
          </label>
          {isRegister && (
            <label className="field">
              Messenger raven (email)
              <input type="email" value={form.email} onChange={update('email')} autoComplete="email" placeholder="mira@guild.org" required />
            </label>
          )}
          <label className="field">
            Secret word
            <input
              type="password"
              value={form.password}
              onChange={update('password')}
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              placeholder="••••••••"
              maxLength={72}
              required
            />
          </label>
          <button className="btn btn-primary btn-block" disabled={submitting}>
            {submitting ? 'One moment…' : isRegister ? 'Sign the register' : 'Enter the Guild Hall'}
          </button>
          <p className="switch-mode">
            {isRegister ? 'Already registered?' : 'New to the guild?'}{' '}
            <button
              type="button"
              className="link-button"
              onClick={() => {
                setMode(isRegister ? 'login' : 'register')
                setError('')
              }}
            >
              {isRegister ? 'Return instead' : 'Register as an adventurer'}
            </button>
          </p>
        </Notice>
      </div>
    </main>
  )
}
