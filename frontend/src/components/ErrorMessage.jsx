// Shows an error in a consistent style, with an optional retry or dismiss button.
export default function ErrorMessage({ message, onRetry, onDismiss }) {
  if (!message) return null
  return (
    <div className="alert alert-error" role="alert">
      <span>{message}</span>
      <span className="alert-actions">
        {onRetry && <button className="btn btn-small" onClick={onRetry}>Try again</button>}
        {onDismiss && (
          <button className="btn btn-ghost btn-small" onClick={onDismiss} aria-label="Dismiss">
            ✕
          </button>
        )}
      </span>
    </div>
  )
}
