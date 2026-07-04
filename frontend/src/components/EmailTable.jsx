import { useState } from "react"
import { useFetch } from "../hooks/useFetch"
import { api } from "../lib/api"

const CATEGORIES = ["billing", "bug_report", "feature_request", "churn_risk", "onboarding", "general_support"]
const URGENCIES  = ["critical", "high", "medium", "low"]
const SENTIMENTS = ["positive", "neutral", "negative"]

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
  const d = new Date(iso)
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
}

function FilterPill({ label, value, active, color, onClick }) {
  return (
    <button
      onClick={onClick}
      style={active ? { background: color, color: "#fff", borderColor: color } : {}}
      className="px-3 py-1 rounded-full text-[0.72rem] font-medium border border-[var(--border)] text-[var(--text-secondary)] transition-all duration-150 hover:border-[var(--text-muted)] cursor-pointer whitespace-nowrap"
    >
      {label}
    </button>
  )
}

function Badge({ value, styleMap, fmtFn = (v) => v }) {
  const s = styleMap[value] ?? {}
  return (
    <span
      className="inline-flex items-center px-2 py-0.5 rounded text-[0.7rem] font-semibold capitalize"
      style={{ color: s.color, background: s.bg ?? "color-mix(in srgb, currentColor 10%, transparent)" }}
    >
      {fmtFn(value)}
    </span>
  )
}

export default function EmailTable({ onSelectEmail, selectedId }) {
  const [filters, setFilters] = useState({ category: null, urgency: null, sentiment: null })

  const { data, loading, error } = useFetch(
    () => api.getEmails({ category: filters.category, urgency: filters.urgency, sentiment: filters.sentiment }),
    [filters.category, filters.urgency, filters.sentiment]
  )

  const toggle = (key, value) =>
    setFilters(f => ({ ...f, [key]: f[key] === value ? null : value }))

  const emails = data?.emails ?? []

  return (
    <div className="px-8 pb-10">
      {/* ── Section header ── */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-[0.72rem] font-semibold tracking-[0.07em] uppercase text-[var(--text-muted)]">
          Inbox
        </h2>
        {!loading && (
          <span className="text-[0.72rem] text-[var(--text-muted)] tabular-nums">
            {emails.length} email{emails.length !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      {/* ── Filters ── */}
      <div className="flex flex-wrap gap-6 mb-4">
        {/* Category */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[0.68rem] uppercase tracking-widest text-[var(--text-muted)] mr-1">Category</span>
          {CATEGORIES.map(c => (
            <FilterPill
              key={c}
              label={fmt(c)}
              value={c}
              active={filters.category === c}
              color={CATEGORY_COLORS[c]}
              onClick={() => toggle("category", c)}
            />
          ))}
        </div>

        {/* Urgency */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[0.68rem] uppercase tracking-widest text-[var(--text-muted)] mr-1">Urgency</span>
          {URGENCIES.map(u => (
            <FilterPill
              key={u}
              label={fmt(u)}
              value={u}
              active={filters.urgency === u}
              color={URGENCY_STYLES[u].color}
              onClick={() => toggle("urgency", u)}
            />
          ))}
        </div>

        {/* Sentiment */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-[0.68rem] uppercase tracking-widest text-[var(--text-muted)] mr-1">Sentiment</span>
          {SENTIMENTS.map(s => (
            <FilterPill
              key={s}
              label={fmt(s)}
              value={s}
              active={filters.sentiment === s}
              color={SENTIMENT_STYLES[s].color}
              onClick={() => toggle("sentiment", s)}
            />
          ))}
        </div>
      </div>

      {/* ── Table ── */}
      <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-[var(--radius)] overflow-hidden shadow-sm">
        {loading && (
          <div className="p-8 text-center text-sm text-[var(--text-muted)]">Loading…</div>
        )}
        {error && (
          <div className="p-8 text-center text-sm text-[var(--accent-red)]">Could not load emails.</div>
        )}
        {!loading && !error && emails.length === 0 && (
          <div className="p-8 text-center text-sm text-[var(--text-muted)]">No emails match the current filters.</div>
        )}
        {!loading && !error && emails.length > 0 && (
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-[var(--border)]">
                {["Sender", "Subject", "Category", "Urgency", "Sentiment", "Received"].map(h => (
                  <th
                    key={h}
                    className="text-left text-[0.68rem] font-semibold tracking-[0.07em] uppercase text-[var(--text-muted)] px-4 py-3 whitespace-nowrap"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {emails.map((email, i) => {
                const isSelected = email.id === selectedId
                return (
                  <tr
                    key={email.id}
                    onClick={() => onSelectEmail(email)}
                    className="cursor-pointer transition-colors duration-100"
                    style={{
                      background: isSelected
                        ? "color-mix(in srgb, var(--accent-blue) 8%, transparent)"
                        : i % 2 === 1 ? "color-mix(in srgb, var(--border) 25%, transparent)" : "transparent",
                      borderLeft: isSelected ? "2px solid var(--accent-blue)" : "2px solid transparent",
                    }}
                    onMouseEnter={e => { if (!isSelected) e.currentTarget.style.background = "color-mix(in srgb, var(--border) 40%, transparent)" }}
                    onMouseLeave={e => { if (!isSelected) e.currentTarget.style.background = i % 2 === 1 ? "color-mix(in srgb, var(--border) 25%, transparent)" : "transparent" }}
                  >
                    {/* Sender */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="font-medium text-[var(--text-primary)] text-[0.82rem]">{email.sender_name}</div>
                      <div className="text-[0.72rem] text-[var(--text-muted)]">{email.sender_company}</div>
                    </td>

                    {/* Subject + summary */}
                    <td className="px-4 py-3 max-w-[280px]">
                      <div className="font-medium text-[var(--text-primary)] text-[0.82rem] truncate">{email.subject}</div>
                      <div className="text-[0.72rem] text-[var(--text-muted)] truncate">{email.summary}</div>
                    </td>

                    {/* Category */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span
                        className="text-[0.7rem] font-semibold capitalize"
                        style={{ color: CATEGORY_COLORS[email.category] ?? "var(--text-secondary)" }}
                      >
                        {fmt(email.category)}
                      </span>
                    </td>

                    {/* Urgency */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      <Badge value={email.urgency} styleMap={URGENCY_STYLES} fmtFn={fmt} />
                    </td>

                    {/* Sentiment */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      <Badge value={email.sentiment} styleMap={SENTIMENT_STYLES} fmtFn={fmt} />
                    </td>

                    {/* Date */}
                    <td className="px-4 py-3 whitespace-nowrap text-[0.72rem] text-[var(--text-muted)] tabular-nums">
                      {formatDate(email.sent_at)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}