import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts"
import { useFetch } from "../../hooks/useFetch"
import { api } from "../../lib/api"

const CATEGORY_COLORS = {
  billing:         "var(--accent-blue)",
  bug_report:      "var(--accent-red)",
  feature_request: "var(--accent-teal)",
  churn_risk:      "var(--accent-amber)",
  onboarding:      "var(--accent-green)",
  general_support: "var(--accent-purple)",
}

const URGENCY_COLORS = {
  critical: "var(--urgency-critical)",
  high:     "var(--urgency-high)",
  medium:   "var(--urgency-medium)",
  low:      "var(--urgency-low)",
}

const SENTIMENT_COLORS = {
  positive: "var(--sentiment-positive)",
  neutral:  "var(--sentiment-neutral)",
  negative: "var(--sentiment-negative)",
}

const formatCategory = (key) =>
  key.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[var(--bg-elevated)] border border-[var(--border)] rounded-md px-3 py-1.5 flex items-center gap-3 shadow-md">
      <span className="text-[0.8rem] text-[var(--text-secondary)] capitalize">{formatCategory(label)}</span>
      <span className="text-[0.9rem] font-bold text-[var(--text-primary)] tabular-nums">{payload[0].value}</span>
    </div>
  )
}

function Panel({ title, children }) {
  return (
    <div className="bg-[var(--bg-surface)] border border-[var(--border)] rounded-[var(--radius)] px-6 py-5 shadow-sm">
      <h3 className="text-[0.72rem] font-semibold tracking-[0.07em] uppercase text-[var(--text-muted)] mb-4">
        {title}
      </h3>
      {children}
    </div>
  )
}

function CategoryChart({ data }) {
  const chartData = Object.entries(data).map(([key, value]) => ({
    name: key, value, fill: CATEGORY_COLORS[key] ?? "var(--accent-blue)",
  }))
  return (
    <Panel title="Emails by Category">
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 16, right: 24, top: 8, bottom: 8 }}>
          <XAxis type="number" tick={{ fontSize: 11, fill: "var(--text-muted)" }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11, fill: "var(--text-secondary)" }} axisLine={false} tickLine={false} tickFormatter={formatCategory} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "var(--bg-elevated)" }} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={20}>
            {chartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Panel>
  )
}

function UrgencyChart({ data }) {
  const order = ["critical", "high", "medium", "low"]
  const chartData = order.filter(k => data[k] !== undefined).map(key => ({
    name: key, value: data[key], fill: URGENCY_COLORS[key],
  }))
  return (
    <Panel title="Emails by Urgency">
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 16, right: 24, top: 8, bottom: 8 }}>
          <XAxis type="number" tick={{ fontSize: 11, fill: "var(--text-muted)" }} axisLine={false} tickLine={false} />
          <YAxis type="category" dataKey="name" width={70} tick={{ fontSize: 11, fill: "var(--text-secondary)" }} axisLine={false} tickLine={false} tickFormatter={s => s.charAt(0).toUpperCase() + s.slice(1)} />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: "var(--bg-elevated)" }} />
          <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={20}>
            {chartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Panel>
  )
}

function SentimentChart({ data }) {
  const chartData = Object.entries(data).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value,
    fill: SENTIMENT_COLORS[key],
  }))
  return (
    <Panel title="Sentiment Distribution">
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie data={chartData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} paddingAngle={3} dataKey="value">
            {chartData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
          </Pie>
          <Tooltip
            formatter={(value, name) => [value, name]}
            contentStyle={{
              background: "var(--bg-surface)", border: "1px solid var(--border)",
              borderRadius: "8px", fontSize: "12px", color: "var(--text-primary)",
            }}
          />
          <Legend
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span style={{ color: "var(--text-secondary)", fontSize: "12px" }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </Panel>
  )
}

export default function Charts() {
  const { data: stats, loading, error } = useFetch(() => api.getStats(), [])

  if (loading) return <div className="p-8 text-center text-sm text-[var(--text-muted)]">Loading charts…</div>
  if (error)   return <div className="p-8 text-center text-sm text-[var(--accent-red)]">Could not load chart data.</div>

  return (
    <div className="flex flex-col gap-4 px-8 pb-6">
      <div className="grid grid-cols-2 gap-4 max-[800px]:grid-cols-1">
        <CategoryChart data={stats.by_category} />
        <UrgencyChart  data={stats.by_urgency} />
      </div>
      <SentimentChart data={stats.by_sentiment} />
    </div>
  )
}