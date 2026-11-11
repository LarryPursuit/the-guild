import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import ErrorMessage from '../components/ErrorMessage'
import GuildCard from '../components/GuildCard'
import GuildForm from '../components/GuildForm'
import Loading from '../components/Loading'
import { tiltFor } from '../components/Notice'

export default function GuildHall() {
  const { user } = useAuth()
  const [guilds, setGuilds] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadGuilds = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      setGuilds(await api.guilds())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadGuilds()
  }, [loadGuilds])

  const createGuild = async (data) => {
    const guild = await api.createGuild(data)
    setGuilds((prev) => [...prev, guild])
  }

  const updateGuild = async (id, data) => {
    const updated = await api.updateGuild(id, data)
    setGuilds((prev) => prev.map((g) => (g.id === id ? updated : g)))
  }

  const deleteGuild = async (guild) => {
    if (!window.confirm(`Disband "${guild.name}"? Its quests will be torn down. Earned loot stays in your pack.`)) return
    try {
      await api.deleteGuild(guild.id)
      setGuilds((prev) => prev.filter((g) => g.id !== guild.id))
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <section>
      <header className="page-header">
        <p className="eyebrow">Guild Hall</p>
        <h1>Well met, {user.username}</h1>
        <p className="muted">Each guild keeps its own board. Choose one to read its requests, or found a new chapter.</p>
      </header>

      <div className="board-layout">
        <div className="corkboard">
          <ErrorMessage message={error} onRetry={loadGuilds} onDismiss={() => setError('')} />
          {loading ? (
            <Loading label="Gathering your guilds…" />
          ) : guilds.length === 0 && !error ? (
            <p className="board-empty">The board is bare. Found your first guild.</p>
          ) : (
            <div className="notice-grid">
              {guilds.map((guild, i) => (
                <GuildCard key={guild.id} guild={guild} tilt={tiltFor(i, 2)} onUpdate={updateGuild} onDelete={deleteGuild} />
              ))}
            </div>
          )}
        </div>

        <aside className="side-panel" aria-labelledby="found-guild">
          <h2 id="found-guild">Found a guild</h2>
          <p className="muted lede">A guild gathers every quest for one goal.</p>
          <GuildForm onSubmit={createGuild} />
        </aside>
      </div>
    </section>
  )
}
