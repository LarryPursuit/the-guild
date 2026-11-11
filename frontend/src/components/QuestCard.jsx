import { useState } from 'react'
import Notice from './Notice'
import { XP_BY_DIFFICULTY } from './QuestForm'

const LABELS = { easy: 'Easy', medium: 'Medium', hard: 'Hard' }
const today = () => new Date().toLocaleDateString('en-CA') // YYYY-MM-DD in local time

function formatDate(isoDate) {
  const [y, m, d] = isoDate.split('-').map(Number)
  return new Date(y, m - 1, d).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

// One quest pinned to the board. Open quests are full notices; cleared ones are smaller and stamped.
export default function QuestCard({ quest, tilt, onComplete, onEdit, onDelete, onClaimReward }) {
  const [busy, setBusy] = useState(false)
  const done = quest.status === 'completed'
  const overdue = !done && quest.due_date && quest.due_date < today()
  const xp = XP_BY_DIFFICULTY[quest.difficulty]

  const run = async (action) => {
    setBusy(true)
    try {
      await action()
    } finally {
      setBusy(false)
    }
  }

  if (done) {
    return (
      <Notice className="notice-cleared" tilt={tilt} pin="pin-grey" pinSize="pin-small">
        <h3>{quest.title}</h3>
        <p className="loot-line">
          +{xp} XP{quest.reward && <> · <strong>Loot: {quest.reward.item_name}</strong></>}
        </p>
        <div className="notice-row" style={{ flexWrap: 'wrap' }}>
          <span className="notice-actions">
            {!quest.reward && (
              <button className="btn btn-small btn-tiny" disabled={busy} onClick={() => run(() => onClaimReward(quest))}>
                {busy ? 'Claiming…' : 'Claim loot'}
              </button>
            )}
            <button className="btn btn-ghost btn-tiny" onClick={() => onEdit(quest)}>Amend</button>
            <button className="btn btn-danger btn-tiny" onClick={() => onDelete(quest)}>Remove</button>
          </span>
          <span className="stamp" aria-label="Completed">COMPLETED</span>
        </div>
      </Notice>
    )
  }

  return (
    <Notice tilt={tilt} pin={`pin-${quest.difficulty}`}>
      <div className="notice-row">
        <span className="request-no">Request No. {String(quest.id).padStart(3, '0')}</span>
        <span className={`difficulty difficulty-${quest.difficulty}`}>{LABELS[quest.difficulty]}</span>
      </div>
      <h3>{quest.title}</h3>
      {quest.description && <p className="notice-details">{quest.description}</p>}
      <div className="notice-meta">
        <span>Bounty <strong>{xp} XP</strong></span>
        {quest.due_date && (
          <span className={overdue ? 'overdue-text' : undefined}>
            {overdue ? 'Overdue · ' : 'Due '}
            {formatDate(quest.due_date)}
          </span>
        )}
      </div>
      <div className="notice-actions">
        <button className="btn btn-primary btn-small" disabled={busy} onClick={() => run(() => onComplete(quest))}>
          {busy ? 'Clearing…' : 'Clear quest'}
        </button>
        <button className="btn btn-ghost btn-small" onClick={() => onEdit(quest)}>Amend</button>
        <button className="btn btn-danger btn-small" onClick={() => onDelete(quest)}>Tear down</button>
      </div>
      {overdue && <span className="overdue-tag" aria-hidden="true">OVERDUE</span>}
    </Notice>
  )
}
