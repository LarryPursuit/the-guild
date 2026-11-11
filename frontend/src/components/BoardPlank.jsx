// The wooden sign nailed across the top of a board section.
export default function BoardPlank({ children, spaced = false }) {
  return (
    <h2 className={`board-plank ${spaced ? 'board-plank-spaced' : ''}`}>
      <span>{children}</span>
    </h2>
  )
}
