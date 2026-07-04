import { useState, useEffect } from "react"

/**
 * Generic data fetching hook.
 *
 * Usage:
 *   const { data, loading, error } = useFetch(() => api.getStats())
 *
 * Re-fetches automatically if deps array changes — same mental model
 * as useEffect's dependency array.
 */
export function useFetch(fetchFn, deps = []) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    let cancelled = false  // prevents state updates if component unmounts mid-fetch

    setLoading(true)
    setError(null)

    fetchFn()
      .then(result => {
        if (!cancelled) {
          setData(result)
          setLoading(false)
        }
      })
      .catch(err => {
        if (!cancelled) {
          setError(err.message)
          setLoading(false)
        }
      })

    return () => { cancelled = true }
  }, deps)

  return { data, loading, error }
}