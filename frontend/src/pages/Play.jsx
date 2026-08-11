import StoryWindow from '../components/StoryWindow'
import MapDisplay from '../components/MapDisplay'
import InfoWindow from '../components/InfoWindow'
import Header from '../components/Header'
import AccountWindow from '../components/AccountWindow'
import { useState } from 'react'

function Play({ onLogout, user, onNavigate }) {
    const [selectedCell, setSelectedCell] = useState(null) // shape: {x, y, biomeData, regionData}
    const [showAccountWindow, setShowAccountWindow] = useState(false)

    return (
        <>
            <Header 
                user={user} 
                setShowAccountWindow={setShowAccountWindow} 
                onNavigate={onNavigate}
            />
            {showAccountWindow && (
                <AccountWindow 
                user={user}
                onLogout={onLogout}
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

export default Play