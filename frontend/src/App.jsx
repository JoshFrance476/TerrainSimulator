import { useState } from 'react'
import StoryWindow from './components/StoryWindow'
import MapDisplay from './components/MapDisplay'
import InfoWindow from './components/InfoWindow'
import Header from './components/Header'

function App() {
  const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData, regionData}

  return (
    <>
      <Header />
      <div className="display">
        <StoryWindow />
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