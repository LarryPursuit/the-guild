import { useState } from 'react'
import { Link } from 'react-router-dom'
import GuildForm from './GuildForm'
import Notice from './Notice'

export default function GuildCard({ guild, tilt, onUpdate, onDelete }) {
  const [editing, setEditing] = useState(false)

  if (editing) {
    return (
      <Notice tilt="0deg">
        <p className="eyebrow">Amending charter</p>
        <GuildForm
          initial={guild}
          submitLabel="Re-pin"
          onSubmit={async (data) => {
            await onUpdate(guild.id, data)
            setEditing(false)
          }}
          onCancel={() => setEditing(false)}
        />
      </Notice>
    )
  }

  return (
    <Notice tilt={tilt}>
      <div className="guild-title">
        <span className="guild-crest" aria-hidden="true">{guild.name[0]?.toUpperCase()}</span>
        <h3><Link to={`/guilds/${guild.id}`}>{guild.name}</Link></h3>
      </div>
      {guild.description && <p className="guild-desc">{guild.description}</p>}
      <p className="guild-stats">
        <span><strong>{guild.open_quests}</strong> open</span>
        <span><strong>{guild.completed_quests}</strong> cleared</span>
      </p>
      <div className="notice-actions">
        <Link className="btn btn-primary btn-small" to={`/guilds/${guild.id}`}>Read the board</Link>
        <button className="btn btn-ghost btn-small" onClick={() => setEditing(true)}>Amend</button>
        <button className="btn btn-danger btn-small" onClick={() => onDelete(guild)}>Disband</button>
      </div>
    </Notice>
  )
}
