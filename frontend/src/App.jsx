import { useState } from 'react'
import ChatWindow from './components/ChatWindow'
import MapDisplay from './components/MapDisplay'

function App() {
  return (
    <div className="display">
      <ChatWindow />
      <MapDisplay />
    </div>
  )
}

export default App