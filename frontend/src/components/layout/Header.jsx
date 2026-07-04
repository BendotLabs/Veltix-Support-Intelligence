import { useEffect, useState } from "react"
import { api } from "../../lib/api"

export default function Header({ theme, onToggleTheme }) {
  const [connected, setConnected] = useState(null)

  useEffect(() => {
    api.getHealth()
      .then(() => setConnected(true))
      .catch(() => setConnected(false))
  }, [])

  const dotColor =
    connected === true  ? "bg-[var(--accent-green)]" :
    connected === false ? "bg-[var(--accent-red)]"   :
                          "bg-[var(--text-muted)]"

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between px-8 h-14 bg-[var(--bg-surface)] border-b border-[var(--border)] shadow-sm">
      {/* Left */}
      <div className="flex items-baseline gap-3">
        <span className="text-xl font-bold tracking-tight text-[var(--text-primary)]">
          <span className="text-[var(--accent-blue)]">V</span>eltix
        </span>
        <span className="text-[0.72rem] font-medium tracking-[0.08em] uppercase text-[var(--text-muted)]">
          Support Intelligence
        </span>
      </div>

      {/* Right */}
      <div className="flex items-center gap-5">
        <div className="flex items-center gap-1.5">
          <span className={`w-[7px] h-[7px] rounded-full transition-colors duration-300 ${dotColor} ${connected === true ? "animate-pulse-dot" : ""}`} />
          <span className="text-[0.75rem] text-[var(--text-muted)] tabular-nums">
            {connected === null && "Connecting…"}
            {connected === true  && "Live"}
            {connected === false && "Offline"}
          </span>
        </div>

        <button
          onClick={onToggleTheme}
          aria-label="Toggle theme"
          title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
          className="w-8 h-8 flex items-center justify-center bg-[var(--bg-elevated)] border border-[var(--border)] rounded-md text-[var(--text-secondary)] text-sm cursor-pointer transition-colors duration-150 hover:bg-[var(--border)] hover:text-[var(--text-primary)]"
        >
          {theme === "dark" ? "☀" : "☾"}
        </button>
      </div>
    </header>
  )
}