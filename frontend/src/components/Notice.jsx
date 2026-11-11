// A paper notice pinned to the cork board. Everything on a board (guilds, quests, loot) uses this.
const TILTS = [-1.6, 1.2, -0.6, 1.8, -1.1, 0.7]

export const tiltFor = (index, offset = 0, scale = 1) => `${TILTS[(index + offset) % TILTS.length] * scale}deg`

export default function Notice({ as: Tag = 'article', tilt = '0deg', pin = '', pinSize = '', className = '', children, ...rest }) {
  return (
    <Tag className={`notice ${className}`} style={{ '--tilt': tilt }} {...rest}>
      <span className={`pin ${pinSize} ${pin}`} aria-hidden="true" />
      {children}
    </Tag>
  )
}
