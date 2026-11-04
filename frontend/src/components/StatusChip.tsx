import type { AppCopy } from './types'
import type { ConnectionState } from '../hooks/useSession'
import styles from './StatusChip.module.css'

type Props = {
  online: boolean
  connectionState: ConnectionState
  serviceMode: string
  copy: AppCopy
}

export default function StatusChip({ online, connectionState, serviceMode, copy }: Props) {
  return (
    <span className={`${styles.chip}${online ? ` ${styles.connected}` : ''}`} role="status" aria-live="polite">
      <span aria-hidden="true" />
      {online
        ? serviceMode === 'LIVE' ? copy.live : copy.sample
        : connectionState === 'reconnecting' ? copy.reconnecting : copy.connecting}
    </span>
  )
}
