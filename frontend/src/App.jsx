import { useState } from 'react'
import SceneWindow from './components/SceneWindow'
import MapDisplay from './components/MapDisplay'
import InfoWindow from './components/InfoWindow'

function App() {
  const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData}
  const [playerLocation, setPlayerLocation] = useState(null) // shape: {x, y}

  return (
    <div className="display">
      <SceneWindow 
        selectedCell={selectedCell}
        playerLocation={playerLocation}
      />
      <InfoWindow 
        selectedCell={selectedCell} 
      />
      <MapDisplay 
        selectedCell={selectedCell}
        onCellSelect={setSelectedCell}
        playerLocation={playerLocation}
        onPlayerLocationChange={setPlayerLocation}
      />
    </div>
  )
}

export default App