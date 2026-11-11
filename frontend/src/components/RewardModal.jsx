import { useEffect } from 'react'
import RankBadge from './RankBadge'

// Shown after clearing a quest: the COMPLETED stamp, XP gained, any promotion, and the loot (or why it failed).
export default function RewardModal({ result, onClose, onClaimReward }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  if (!result) return null
  const { quest, xp_gained, user, ranked_up, reward, reward_error } = result

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="reward-title" onClick={(e) => e.stopPropagation()}>
        <span className="pin pin-large pin-red" aria-hidden="true" />
        <p className="eyebrow">Quest cleared</p>
        <h2 id="reward-title">{quest.title}</h2>
        <div className="stamp-row"><span className="stamp stamp-large">COMPLETED</span></div>
        <p className="xp-gain">+{xp_gained} XP</p>

        {ranked_up && (
          <p className="rank-up">
            The guild promotes you to <RankBadge rank={user.rank} />
          </p>
        )}

        {reward ? (
          <div className="loot-box">
            <p className="eyebrow">Loot found</p>
            <p className="loot-name">{reward.item_name}</p>
            {reward.item_category && <p className="muted">{reward.item_category}</p>}
          </div>
        ) : (
          <div className="alert alert-warning">
            <span>{reward_error || 'No loot this time.'}</span>
            <button className="btn btn-small" onClick={() => onClaimReward(quest)}>Try again</button>
          </div>
        )}

        <button className="btn btn-primary" onClick={onClose} autoFocus>Back to the quest board</button>
      </div>
    </div>
  )
}
