import { useState } from 'react'

// Used for both founding and amending a guild.
export default function GuildForm({ initial = {}, submitLabel = 'Raise the banner', onSubmit, onCancel }) {
  const [name, setName] = useState(initial.name || '')
  const [description, setDescription] = useState(initial.description || '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!name.trim()) {
      setError('A guild needs a name.')
      return
    }
    setSaving(true)
    setError('')
    try {
      await onSubmit({ name: name.trim(), description: description.trim() || null })
      if (!initial.name) {
        setName('')
        setDescription('')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <label>
        Guild name
        <input value={name} onChange={(e) => setName(e.target.value)} maxLength={100} placeholder="Iron Body Guild" />
      </label>
      <label>
        <span>Charter <span className="optional">(optional)</span></span>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={1000}
          rows={2}
          placeholder="Training, sleep and proper meals"
        />
      </label>
      {error && <p className="field-error" role="alert">{error}</p>}
      <div className="form-actions">
        <button className={onCancel ? 'btn btn-primary btn-small' : 'btn btn-primary'} disabled={saving}>
          {saving ? 'Saving…' : submitLabel}
        </button>
        {onCancel && <button type="button" className="btn btn-ghost btn-small" onClick={onCancel}>Cancel</button>}
      </div>
    </form>
  )
}
