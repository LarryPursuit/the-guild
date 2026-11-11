import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../context/AuthContext'
import ErrorMessage from '../components/ErrorMessage'
import Loading from '../components/Loading'
import Notice, { tiltFor } from '../components/Notice'
import RankBadge from '../components/RankBadge'

const RANK_FLOORS = { Copper: 0, Silver: 100, Gold: 300, Mythril: 600 }

const formatSince = (iso) =>
  iso ? new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) : '—'

export default function AdventurerProfile() {
  const { user, setUser } = useAuth()
  const [classes, setClasses] = useState([])
  const [classError, setClassError] = useState('')
  const [rewards, setRewards] = useState([])
  const [rewardsError, setRewardsError] = useState('')
  const [loadingRewards, setLoadingRewards] = useState(true)
  const [savingClass, setSavingClass] = useState(false)

  const loadClasses = useCallback(async () => {
    setClassError('')
    try {
      setClasses(await api.classes())
    } catch (err) {
      setClassError(err.message)
    }
  }, [])

  const loadRewards = useCallback(async () => {
    setLoadingRewards(true)
    setRewardsError('')
    try {
      setRewards(await api.rewards())
    } catch (err) {
      setRewardsError(err.message)
    } finally {
      setLoadingRewards(false)
    }
  }, [])

  useEffect(() => {
    loadClasses()
    loadRewards()
    api.me().then(setUser).catch(() => {}) // refresh XP in case it changed elsewhere
  }, [loadClasses, loadRewards, setUser])

  const chooseClass = async (index) => {
    setSavingClass(true)
    setClassError('')
    try {
      setUser(await api.updateMe({ character_class: index }))
    } catch (err) {
      setClassError(err.message)
    } finally {
      setSavingClass(false)
    }
  }

  // Progress toward the next rank, as a percentage.
  const floor = RANK_FLOORS[user.rank] ?? 0
  const progress = user.next_rank_xp ? Math.round(((user.xp - floor) / (user.next_rank_xp - floor)) * 100) : 100
  const rankKey = user.rank?.toLowerCase()

  return (
    <section>
      <header className="page-header">
        <p className="eyebrow">Adventurer</p>
        <h1>Guild License</h1>
      </header>

      <div className="license-layout">
        <article className={`license license-${rankKey}`} aria-label="Guild license">
          <div className="license-head">
            <span><span className="brand-mark" aria-hidden="true">⚔</span> Adventurers&apos; Guild · License</span>
            <span className="license-no">No. {String(user.id).padStart(4, '0')}</span>
          </div>
          <div className="license-body">
            <div className="license-portrait" aria-hidden="true">{user.username[0]?.toUpperCase()}</div>
            <dl className="license-fields">
              <div><dt>Name</dt><dd className="big">{user.username}</dd></div>
              <div><dt>Class</dt><dd className="big">{user.character_class || 'Unchosen'}</dd></div>
              <div><dt>Rank</dt><dd className="badge"><RankBadge rank={user.rank} /></dd></div>
              <div><dt>Registered</dt><dd>{formatSince(user.created_at)}</dd></div>
              <div><dt>Quests cleared</dt><dd>{user.quests_completed ?? 0}</dd></div>
              <div><dt>Experience</dt><dd>{user.xp} XP</dd></div>
            </dl>
          </div>
          <div className="license-progress">
            <div className="progress" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress}
              aria-label={user.next_rank ? `Progress to ${user.next_rank}` : 'Rank progress'}>
              <div className="progress-bar" style={{ width: `${progress}%` }} />
            </div>
            <p className="muted">
              {user.next_rank
                ? `${user.next_rank_xp - user.xp} XP until ${user.next_rank}`
                : 'Highest rank reached. Legendary.'}
            </p>
          </div>
          <div className="guild-seal" aria-hidden="true">GUILD<br /><span className="mark">⚔</span><br />SEAL</div>
        </article>

        <section className="side-panel calling" aria-labelledby="calling-title">
          <h2 id="calling-title">Calling</h2>
          <p className="muted">Classes come from the D&amp;D 5e API. Your choice is printed on your license.</p>
          <ErrorMessage message={classError} onRetry={classes.length ? undefined : loadClasses} />
          {classes.length === 0 && !classError ? (
            <Loading label="Consulting the archives…" />
          ) : (
            <div className="class-chips">
              {classes.map((c) => (
                <button
                  key={c.index}
                  className="class-chip"
                  aria-pressed={c.name === user.character_class}
                  disabled={savingClass}
                  onClick={() => chooseClass(c.index)}
                >
                  {c.name}
                </button>
              ))}
            </div>
          )}
        </section>
      </div>

      <section aria-labelledby="pack-title">
        <h2 className="section-title" id="pack-title">Pack <span className="count">{rewards.length}</span></h2>
        <div className="corkboard corkboard-compact">
          <ErrorMessage message={rewardsError} onRetry={loadRewards} />
          {loadingRewards ? (
            <Loading label="Opening your pack…" />
          ) : rewards.length === 0 && !rewardsError ? (
            <p className="board-empty">Your pack is empty. Clear quests to earn loot.</p>
          ) : (
            <ul className="notice-grid notice-grid-pack">
              {rewards.map((r, i) => (
                <Notice as="li" key={r.id} className="notice-item" tilt={tiltFor(i, 1, 0.8)} pin="pin-amber" pinSize="pin-small">
                  <span className="loot-name">{r.item_name}</span>
                  <span className="muted">{r.item_category || 'Item'}</span>
                </Notice>
              ))}
            </ul>
          )}
        </div>
      </section>
    </section>
  )
}
