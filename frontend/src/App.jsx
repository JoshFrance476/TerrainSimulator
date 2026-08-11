import { useState, useEffect } from 'react'
import Landing from './pages/Landing'
import Play from './pages/Play'

function App() {
  const [user, setUser] = useState(undefined); // undefined = loading, null = logged out
  const [page, setPage] = useState("landing");

  useEffect(() => {
    const fetchUser = async () => {
      const res = await fetch('/api/auth/me', { credentials: 'include' })
      if (res.ok) {
        const userData = await res.json()
        setUser(userData)
      }
    }
    fetchUser()
  }, [])

  const handleLogout = async () => {
    await fetch('/api/auth/logout', { method: 'POST', credentials: 'include' })
    window.location.reload()
  }

  if (user === undefined) {
    return (
      <div className="loading-screen">
        <p>Loading...</p>
      </div>
    )
  }

  return (
    <>
      {page === "landing" && <Landing onLogout={handleLogout} user={user} onNavigate={setPage}/>}
      {page === "play" && <Play user={user} onNavigate={setPage}/>} 
    </>
  )
}

export default App