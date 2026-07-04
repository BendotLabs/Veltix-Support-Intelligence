import { api } from "../lib/api"
import { useFetch } from "../hooks/useFetch"

const CARDS = [
  { key: "total",    label: "Total Emails",      getValue: (s) => s.total_emails,             accent: "var(--accent-blue)"   },
  { key: "critical", label: "Critical",           getValue: (s) => s.by_urgency?.critical ?? 0, accent: "var(--accent-red)"    },
  { key: "churn",    label: "Churn Risk",         getValue: (s) => s.by_category?.churn_risk ?? 0, accent: "var(--accent-amber)"  },
  { key: "negative", label: "Negative Sentiment", getValue: (s) => s.by_sentiment?.negative ?? 0,  accent: "var(--accent-purple)" },
]

function Card({ label, value, accent, loading }) {
  return (
    <div className="relative bg-[var(--bg-surface)] border border-[var(--border)] rounded-[var(--radius)] px-6 pt-5 pb-6 shadow-sm overflow-hidden flex flex-col gap-1.5 transition-all duration-150 hover:-translate-y-px hover:shadow-md group">
      <span className="text-[0.72rem] font-semibold tracking-[0.07em] uppercase text-[var(--text-muted)]">
        {label}
      </span>
      <span className="text-[2.25rem] font-bold tracking-[-0.03em] leading-none tabular-nums" style={{ color: accent }}>
        {loading ? "—" : value}
      </span>
      {/* Accent bar */}
      <div
        className="absolute bottom-0 left-0 h-[3px] w-[40%] rounded-tr-sm transition-all duration-150 group-hover:w-full"
        style={{ background: accent }}
      />
    </div>
  )
}

export default function StatCards() {
  const { data: stats, loading } = useFetch(() => api.getStats(), [])

  return (
    <div className="grid grid-cols-4 gap-4 px-8 py-6 max-[900px]:grid-cols-2 max-[500px]:grid-cols-1">
      {CARDS.map(card => (
        <Card
          key={card.key}
          label={card.label}
          value={stats ? card.getValue(stats) : null}
          accent={card.accent}
          loading={loading}
        />
      ))}
    </div>
  )
}