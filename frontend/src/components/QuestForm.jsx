import { useState } from 'react'

export const XP_BY_DIFFICULTY = { easy: 10, medium: 25, hard: 50 }
const LABELS = { easy: 'Easy', medium: 'Medium', hard: 'Hard' }

// The front-desk form beside the quest board. Posts a new notice, or amends one when `initial` is a quest.
export default function QuestForm({ initial = null, onSubmit, onCancel }) {
  const editing = Boolean(initial)
  const lockDifficulty = initial?.status === 'completed' // XP was already paid out
  const [form, setForm] = useState({
    title: initial?.title || '',
    description: initial?.description || '',
    difficulty: initial?.difficulty || 'easy',
    due_date: initial?.due_date || '',
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const update = (field) => (e) => setForm({ ...form, [field]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.title.trim()) {
      setError('Every quest needs a title.')
      return
    }
    setSaving(true)
    setError('')
    try {
      const body = {
        title: form.title.trim(),
        description: form.description.trim() || null,
        due_date: form.due_date || null,
      }
      if (!lockDifficulty) body.difficulty = form.difficulty
      await onSubmit(body)
      if (!editing) setForm({ title: '', description: '', difficulty: 'easy', due_date: '' })
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="panel-head" style={{ marginBottom: 0 }}>
        <p className="eyebrow">{editing ? 'Amending notice' : 'Front desk'}</p>
        <h2>{editing ? 'Amend the notice' : 'Post a notice'}</h2>
      </div>
      <label>
        Request
        <input value={form.title} onChange={update('title')} maxLength={200} placeholder="Finish the Project 2 pitch" />
      </label>
      <fieldset className="field">
        <legend>Danger rating</legend>
        <div className="danger-picker">
          {Object.entries(XP_BY_DIFFICULTY).map(([level, xp]) => (
            <button
              key={level}
              type="button"
              className={`danger-option difficulty-${level}`}
              aria-pressed={form.difficulty === level}
              disabled={lockDifficulty}
              onClick={() => setForm({ ...form, difficulty: level })}
            >
              <span className="label">{LABELS[level]}</span>
              <span className="xp">{xp} XP</span>
            </button>
          ))}
        </div>
      </fieldset>
      <label>
        <span>Due by <span className="optional">(optional)</span></span>
        <input type="date" value={form.due_date} onChange={update('due_date')} />
      </label>
      <label>
        <span>Details <span className="optional">(optional)</span></span>
        <textarea value={form.description} onChange={update('description')} maxLength={2000} rows={2} />
      </label>
      {error && <p className="field-error" role="alert">{error}</p>}
      <div className="form-actions">
        <button className="btn btn-primary" disabled={saving}>
          {saving ? 'Pinning…' : editing ? 'Re-pin notice' : 'Pin to the board'}
        </button>
        {onCancel && <button type="button" className="btn btn-ghost" onClick={onCancel}>Cancel</button>}
      </div>
    </form>
  )
}
