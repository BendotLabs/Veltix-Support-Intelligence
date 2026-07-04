import { useState, useEffect } from "react"
import Header from "./components/layout/Header"
import StatCards from "./components/StatCards"
import Charts from "./components/charts/Charts"
import EmailTable from "./components/EmailTable"
import EmailPanel from "./components/EmailPanel"
import "./index.css"

export default function App() {
  const [theme, setTheme] = useState(
    () => localStorage.getItem("veltix-theme") || "dark"
  )
  const [selectedEmail, setSelectedEmail] = useState(null)

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme)
    localStorage.setItem("veltix-theme", theme)
  }, [theme])

  const toggleTheme = () => setTheme(t => t === "dark" ? "light" : "dark")

  return (
    <div className="min-h-screen bg-[var(--bg-base)]">
      <Header theme={theme} onToggleTheme={toggleTheme} />
      <main className="max-w-[1400px] mx-auto">
        <StatCards />
        <Charts />
        <EmailTable
          onSelectEmail={setSelectedEmail}
          selectedId={selectedEmail?.id ?? null}
        />
      </main>

      {selectedEmail && (
        <EmailPanel
          emailId={selectedEmail.id}
          onClose={() => setSelectedEmail(null)}
        />
      )}
    </div>
  )
}