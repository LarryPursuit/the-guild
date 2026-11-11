import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import BoardPlank from '../components/BoardPlank'
import ErrorMessage from '../components/ErrorMessage'
import Loading from '../components/Loading'
import { tiltFor } from '../components/Notice'
import QuestCard from '../components/QuestCard'
import QuestForm from '../components/QuestForm'
import RewardModal from '../components/RewardModal'

export default function GuildPage() {
  const { guildId } = useParams()
  const { setUser } = useAuth()
  const [guild, setGuild] = useState(null)
  const [quests, setQuests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notFound, setNotFound] = useState(false)
  const [editing, setEditing] = useState(null) // the quest being amended in the side form
  const [result, setResult] = useState(null) // last quest-completion result, for the modal

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    setNotFound(false)
    try {
      const [g, q] = await Promise.all([api.guild(guildId), api.quests(guildId)])
      setGuild(g)
      setQuests(q)
    } catch (err) {
      if (err.status === 404) setNotFound(true)
      else setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [guildId])

  useEffect(() => {
    load()
  }, [load])

  const replaceQuest = (updated) => setQuests((prev) => prev.map((q) => (q.id === updated.id ? { ...q, ...updated } : q)))

  const saveQuest = async (data) => {
    if (editing) {
      replaceQuest(await api.updateQuest(editing.id, data))
      setEditing(null)
    } else {
      const quest = await api.createQuest(guildId, data)
      setQuests((prev) => [...prev, quest])
    }
  }

  const startEdit = (quest) => {
    setEditing(quest)
    // On narrow screens the form sits above the board, so bring it into view.
    document.getElementById('quest-desk')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }

  const deleteQuest = async (quest) => {
    if (!window.confirm(`Tear down "${quest.title}"?`)) return
    try {
      await api.deleteQuest(quest.id)
      setQuests((prev) => prev.filter((q) => q.id !== quest.id))
      if (editing?.id === quest.id) setEditing(null)
    } catch (err) {
      setError(err.message)
    }
  }

  const completeQuest = async (quest) => {
    try {
      const res = await api.completeQuest(quest.id)
      replaceQuest({ ...res.quest, reward: res.reward })
      setUser(res.user)
      if (editing?.id === quest.id) setEditing(null)
      setResult(res)
    } catch (err) {
      setError(err.message)
    }
  }

  // Retry the loot if the D&D API failed the first time.
  const claimReward = async (quest) => {
    try {
      const reward = await api.claimReward(quest.id)
      setQuests((prev) => prev.map((q) => (q.id === quest.id ? { ...q, reward } : q)))
      setResult((prev) => (prev && prev.quest.id === quest.id ? { ...prev, reward, reward_error: null } : prev))
    } catch (err) {
      if (result && result.quest.id === quest.id) setResult({ ...result, reward_error: err.message })
      else setError(err.message)
    }
  }

  if (loading) return <Loading label="Unrolling the quest board…" />
  if (notFound) {
    return (
      <div className="empty-state">
        <h2>Guild not found</h2>
        <p className="muted">It may have been disbanded.</p>
        <Link className="btn" to="/">Back to the Guild Hall</Link>
      </div>
    )
  }

  const open = quests.filter((q) => q.status === 'open')
  const completed = quests.filter((q) => q.status === 'completed')
  const cardProps = { onComplete: completeQuest, onEdit: startEdit, onDelete: deleteQuest, onClaimReward: claimReward }

  return (
    <section>
      <Link to="/" className="back-link">← Guild Hall</Link>
      {guild && (
        <header className="page-header">
          <p className="eyebrow">Quest board</p>
          <h1>{guild.name}</h1>
          {guild.description && <p className="muted">{guild.description}</p>}
        </header>
      )}

      <div className="board-layout">
        <div className="corkboard corkboard-quests">
          <ErrorMessage message={error} onRetry={guild ? undefined : load} onDismiss={() => setError('')} />

          <BoardPlank>Open requests · {open.length}</BoardPlank>
          {open.length === 0 ? (
            <p className="board-empty">No open requests. Pin a notice to begin.</p>
          ) : (
            <div className="notice-grid notice-grid-quests">
              {open.map((q, i) => <QuestCard key={q.id} quest={q} tilt={tiltFor(i)} {...cardProps} />)}
            </div>
          )}

          <BoardPlank spaced>Cleared · {completed.length}</BoardPlank>
          {completed.length === 0 ? (
            <p className="board-empty board-empty-plain">Cleared notices and their loot are kept here.</p>
          ) : (
            <div className="notice-grid notice-grid-cleared">
              {completed.map((q, i) => <QuestCard key={q.id} quest={q} tilt={tiltFor(i, 3)} {...cardProps} />)}
            </div>
          )}
        </div>

        <aside className="side-panel" id="quest-desk" aria-label="Quest form">
          <QuestForm
            key={editing ? `edit-${editing.id}` : 'new'}
            initial={editing}
            onSubmit={saveQuest}
            onCancel={editing ? () => setEditing(null) : undefined}
          />
        </aside>
      </div>

      <RewardModal result={result} onClose={() => setResult(null)} onClaimReward={claimReward} />
    </section>
  )
}
