import { useState } from 'react'
import StoryWindow from './components/StoryWindow'
import MapDisplay from './components/MapDisplay'
import InfoWindow from './components/InfoWindow'
import { WorldDataProvider } from './contexts/WorldDataContext'
import { StoryDataProvider } from './contexts/StoryDataContext'

function App() {
  const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData, regionData}
  const [playerLocation, setPlayerLocation] = useState(null) // shape: {x, y}

  return (
    <WorldDataProvider>
      <StoryDataProvider>
        <div className="display">
          <StoryWindow 
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
      </StoryDataProvider>
    </WorldDataProvider>
  )
}

export default App