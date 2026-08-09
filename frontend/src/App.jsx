import { useState, useEffect } from 'react'
import StoryWindow from './components/StoryWindow'
import MapDisplay from './components/MapDisplay'
import InfoWindow from './components/InfoWindow'
import Header from './components/Header'
import AccountWindow from './components/AccountWindow'

function App() {
  const [user, setUser] = useState(undefined) // undefined = loading, null = logged out
  const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData, regionData}
  const [showAccountWindow, setShowAccountWindow] = useState(false)

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
      <Header 
        user={user} 
        setShowAccountWindow={setShowAccountWindow} 
      />
      {showAccountWindow && (
        <AccountWindow 
          user={user}
          onLogout={handleLogout}
        />
      )}
      <div className="display">
        <StoryWindow user={user} />
        <InfoWindow 
          selectedCell={selectedCell} 
        />
        <MapDisplay 
          selectedCell={selectedCell}
          onCellSelect={setSelectedCell}
        />
      </div>
    </>
  )
}

export default App