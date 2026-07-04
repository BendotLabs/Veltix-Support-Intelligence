import { useEffect } from "react"
import { useFetch } from "../hooks/useFetch"
import { api } from "../lib/api"

const URGENCY_STYLES = {
  critical: { color: "var(--urgency-critical)", bg: "color-mix(in srgb, var(--urgency-critical) 12%, transparent)" },
  high:     { color: "var(--urgency-high)",     bg: "color-mix(in srgb, var(--urgency-high) 12%, transparent)" },
  medium:   { color: "var(--urgency-medium)",   bg: "color-mix(in srgb, var(--urgency-medium) 12%, transparent)" },
  low:      { color: "var(--urgency-low)",      bg: "color-mix(in srgb, var(--urgency-low) 12%, transparent)" },
}

const SENTIMENT_STYLES = {
  positive: { color: "var(--sentiment-positive)" },
  neutral:  { color: "var(--sentiment-neutral)" },
  negative: { color: "var(--sentiment-negative)" },
}

const CATEGORY_COLORS = {
  billing:         "var(--accent-blue)",
  bug_report:      "var(--accent-red)",
  feature_request: "var(--accent-teal)",
  churn_risk:      "var(--accent-amber)",
  onboarding:      "var(--accent-green)",
  general_support: "var(--accent-purple)",
}

const fmt = (key) => key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())

const formatDate = (iso) => {
  if (!iso) return "—"
  return new Date(iso).toLocaleString("en-US", {
    month: "long", day: "numeric", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  })
}

function Badge({ value, styleMap, fmtFn = v => v }) {
  const s = styleMap[value] ?? {}
  return (
    <span
      className="inline-flex items-center px-2.5 py-1 rounded text-[0.72rem] font-semibold capitalize"
      style={{ color: s.color, background: s.bg ?? "color-mix(in srgb, currentColor 10%, transparent)" }}
    >
      {fmtFn(value)}
    </span>
  )
}

function Field({ label, children }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-[0.65rem] font-semibold tracking-[0.08em] uppercase text-[var(--text-muted)]">
        {label}
      </span>
      <div className="text-[0.82rem] text-[var(--text-primary)]">{children}</div>
    </div>
  )
}

export default function EmailPanel({ emailId, onClose }) {
  const { data: email, loading, error } = useFetch(
    () => api.getEmail(emailId),
    [emailId]
  )

  // Close on Escape key
  useEffect(() => {
    const handler = (e) => { if (e.key === "Escape") onClose() }
    window.addEventListener("keydown", handler)
    return () => window.removeEventListener("keydown", handler)
  }, [onClose])

  return (
    <>
      {/* Backdrop — clicking closes the panel */}
      <div
        className="fixed inset-0 z-30"
        onClick={onClose}
      />

      {/* Panel */}
      <aside
        className="fixed top-14 right-0 bottom-0 z-40 flex flex-col overflow-hidden"
        style={{
          width: "min(480px, 100vw)",
          background: "var(--bg-surface)",
          borderLeft: "1px solid var(--border)",
          boxShadow: "var(--shadow-md)",
        }}
      >
        {/* ── Panel header ── */}
        <div
          className="flex items-center justify-between px-5 py-3 shrink-0"
          style={{ borderBottom: "1px solid var(--border)" }}
        >
          <span className="text-[0.72rem] font-semibold tracking-[0.07em] uppercase text-[var(--text-muted)]">
            Email Detail
          </span>
          <button
            onClick={onClose}
            aria-label="Close panel"
            className="w-7 h-7 flex items-center justify-center rounded text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-elevated)] transition-colors duration-150 cursor-pointer text-lg leading-none"
          >
            ×
          </button>
        </div>

        {/* ── Content ── */}
        <div className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-5">
          {loading && (
            <div className="flex-1 flex items-center justify-center text-sm text-[var(--text-muted)]">
              Loading…
            </div>
          )}

          {error && (
            <div className="flex-1 flex items-center justify-center text-sm text-[var(--accent-red)]">
              Could not load email.
            </div>
          )}

          {email && !loading && (
            <>
              {/* Subject */}
              <div>
                <h2 className="text-[1rem] font-semibold text-[var(--text-primary)] leading-snug">
                  {email.subject}
                </h2>
              </div>

              {/* Sender info */}
              <div
                className="rounded-[var(--radius)] px-4 py-3 flex flex-col gap-1"
                style={{ background: "var(--bg-elevated)", border: "1px solid var(--border)" }}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-[0.85rem] text-[var(--text-primary)]">{email.sender_name}</span>
                  <span
                    className="text-[0.65rem] font-semibold px-2 py-0.5 rounded"
                    style={{
                      color: CATEGORY_COLORS[email.category] ?? "var(--text-muted)",
                      background: "color-mix(in srgb, currentColor 10%, transparent)",
                    }}
                  >
                    {email.subscription_tier}
                  </span>
                </div>
                <span className="text-[0.75rem] text-[var(--text-muted)]">{email.sender_email}</span>
                <span className="text-[0.75rem] text-[var(--text-muted)]">{email.sender_company}</span>
                <span className="text-[0.72rem] text-[var(--text-muted)] mt-1">{formatDate(email.sent_at)}</span>
              </div>

              {/* AI tags row */}
              <div className="flex flex-wrap gap-2">
                <Badge value={email.urgency}   styleMap={URGENCY_STYLES}  fmtFn={fmt} />
                <Badge value={email.sentiment} styleMap={SENTIMENT_STYLES} fmtFn={fmt} />
                <span
                  className="inline-flex items-center px-2.5 py-1 rounded text-[0.72rem] font-semibold capitalize"
                  style={{ color: CATEGORY_COLORS[email.category], background: "color-mix(in srgb, currentColor 10%, transparent)" }}
                >
                  {fmt(email.category)}
                </span>
              </div>

              {/* Summary + action */}
              <div className="flex flex-col gap-3">
                <Field label="AI Summary">{email.summary}</Field>
                <Field label="Action Required">
                  <span className="text-[var(--accent-amber)]">{email.action_required}</span>
                </Field>
              </div>

              {/* Key topics */}
              {email.key_topics?.length > 0 && (
                <div className="flex flex-col gap-1.5">
                  <span className="text-[0.65rem] font-semibold tracking-[0.08em] uppercase text-[var(--text-muted)]">
                    Key Topics
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {email.key_topics.map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 text-[0.7rem] rounded"
                        style={{ background: "var(--bg-elevated)", border: "1px solid var(--border)", color: "var(--text-secondary)" }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Divider */}
              <div style={{ borderTop: "1px solid var(--border)" }} />

              {/* Full email body */}
              <div className="flex flex-col gap-2">
                <span className="text-[0.65rem] font-semibold tracking-[0.08em] uppercase text-[var(--text-muted)]">
                  Email Body
                </span>
                <pre
                  className="text-[0.8rem] text-[var(--text-secondary)] whitespace-pre-wrap leading-relaxed font-[inherit]"
                >
                  {email.body}
                </pre>
              </div>
            </>
          )}
        </div>
      </aside>
    </>
  )
}