import { useState } from 'react'
import ChatWindow from './components/ChatWindow'
import MapDisplay from './components/MapDisplay'
import InfoWindow from './components/InfoWindow'

function App() {
  const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData}

  return (
    <div className="display">
      <ChatWindow 
        selectedCell={selectedCell}
      />
      <InfoWindow 
        selectedCell={selectedCell} 
      />
      <MapDisplay 
        selectedCell={selectedCell}
        onCellSelect={setSelectedCell}
      />
    </div>
  )
}

export default App