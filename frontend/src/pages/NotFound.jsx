import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="empty-state">
      <h1>Lost in the wilds</h1>
      <p className="muted">That page doesn't exist.</p>
      <Link className="btn" to="/">Return to the Guild Hall</Link>
    </div>
  )
}
