import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api, tokenStore } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  // "checking" while we verify a saved token on page load
  const [checking, setChecking] = useState(Boolean(tokenStore.get()))

  const logout = useCallback(() => {
    tokenStore.clear()
    setUser(null)
  }, [])

  // On first load, if a token is saved, fetch the user it belongs to.
  useEffect(() => {
    if (!tokenStore.get()) return
    api
      .me()
      .then(setUser)
      .catch(() => logout())
      .finally(() => setChecking(false))
  }, [logout])

  // api.js fires this event when the server says the token is no longer valid.
  useEffect(() => {
    window.addEventListener('guild:logout', logout)
    return () => window.removeEventListener('guild:logout', logout)
  }, [logout])

  const handleAuth = (data) => {
    tokenStore.set(data.access_token)
    setUser(data.user)
    return data.user
  }

  const login = async (username, password) => handleAuth(await api.login({ username, password }))
  const register = async (form) => handleAuth(await api.register(form))
  const demo = async () => handleAuth(await api.demo())

  return (
    <AuthContext.Provider value={{ user, setUser, checking, login, register, demo, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
