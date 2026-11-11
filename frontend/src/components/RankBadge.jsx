export default function RankBadge({ rank }) {
  return <span className={`rank-badge rank-${rank?.toLowerCase()}`}>{rank}</span>
}
