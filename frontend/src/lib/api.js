const BASE_URL = "http://localhost:8000"

async function request(path, params = {}) {
  const url = new URL(`${BASE_URL}${path}`)

  // Append any query params cleanly — skips undefined/null values
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.append(key, value)
    }
  })

  const res = await fetch(url)
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`)
  return res.json()
}

export const api = {
  getStats:  ()                => request("/stats"),
  getEmails: (filters = {})   => request("/emails", filters),
  getEmail:  (id)              => request(`/emails/${id}`),
  getHealth: ()                => request("/health"),
};