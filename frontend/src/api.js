// One place for every call to the FastAPI backend.
// Each function returns parsed JSON or throws an ApiError with a readable message.

const BASE_URL = import.meta.env.VITE_API_URL || ''
const TOKEN_KEY = 'guild_token'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

async function request(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = tokenStore.get()
  if (token) headers.Authorization = `Bearer ${token}`

  let response
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError("Can't reach the server. Is the backend running?", 0)
  }

  if (response.status === 204) return null

  let data = null
  try {
    data = await response.json()
  } catch {
    // Non-JSON response (e.g. a proxy error page)
  }

  if (!response.ok) {
    if (response.status === 401 && token) {
      // Token expired or invalid: tell the app to log out.
      window.dispatchEvent(new Event('guild:logout'))
    }
    const message = typeof data?.detail === 'string' ? data.detail : `Request failed (${response.status}).`
    throw new ApiError(message, response.status)
  }
  return data
}

export const api = {
  // Auth
  register: (body) => request('/api/auth/register', { method: 'POST', body }),
  login: (body) => request('/api/auth/login', { method: 'POST', body }),

  // Adventurer
  me: () => request('/api/users/me'),
  updateMe: (body) => request('/api/users/me', { method: 'PATCH', body }),
  classes: () => request('/api/classes'),
  rewards: () => request('/api/rewards'),

  // Guilds
  guilds: () => request('/api/guilds'),
  guild: (id) => request(`/api/guilds/${id}`),
  createGuild: (body) => request('/api/guilds', { method: 'POST', body }),
  updateGuild: (id, body) => request(`/api/guilds/${id}`, { method: 'PATCH', body }),
  deleteGuild: (id) => request(`/api/guilds/${id}`, { method: 'DELETE' }),

  // Quests
  quests: (guildId) => request(`/api/guilds/${guildId}/quests`),
  createQuest: (guildId, body) => request(`/api/guilds/${guildId}/quests`, { method: 'POST', body }),
  updateQuest: (id, body) => request(`/api/quests/${id}`, { method: 'PATCH', body }),
  deleteQuest: (id) => request(`/api/quests/${id}`, { method: 'DELETE' }),
  completeQuest: (id) => request(`/api/quests/${id}/complete`, { method: 'POST' }),
  claimReward: (id) => request(`/api/quests/${id}/reward`, { method: 'POST' }),
}
