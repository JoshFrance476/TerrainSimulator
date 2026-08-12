import './landing.css'
import { useWorldsQuery , useNewSessionMutation} from '../queries/queries'
import PlaySetupModal from '../components/PlaySetupModal'
import { useState } from 'react';

function Landing({ onNavigate }) {
    const {data: worlds, isLoading, isError} = useWorldsQuery();
    const [showPlaySetupModal, setShowPlaySetupModal] = useState(false);
    const [worldMetadata, setWorldMetadata] = useState(null)
    const newSession = useNewSessionMutation()

    function handlePlay(world) {
        setWorldMetadata(world)
        setShowPlaySetupModal(true);
        newSession.mutate(world.id)
    }

    return (
        <div className="landing-page">
            <div className="main-section">
                <h1 className="main-title">Welcome to Sandbox</h1>
                <h2 className="main-subtitle">A platform for procedural text-based open-world story games, powered by generative AI</h2>
                <div className="main-navigation">
                    <button className="main-button" onClick={() => onNavigate("play")}>Load existing playthrough</button>
                    <button className="main-button">Start new playthrough</button>
                    <button className="main-button">Open editor</button>
                </div>
            </div>
            <div className="browser">
                {isLoading && <p>Loading worlds...</p>}
                {isError && <p>Error loading worlds</p>}
                {worlds && worlds.length === 0 && <p>No worlds available</p>}
                {worlds && worlds.length > 0 && (
                    <ul className="world-list">
                    {worlds.map(world => (
                        <li key={world.id} className="world-list-item">
                            <img src={`/api/worlds/${world.id}/thumbnail`} />
                            <div className="world-list-item-body">
                                <h2 className="world-list-item-title">{world.name}</h2>
                                <p className="world-list-item-description">{world.description}</p>
                                <div className="world-list-item-actions">
                                    <button className="world-list-item-button" onClick={() => handlePlay(world)}>Play</button>
                                    <button className="world-list-item-button">Load in Editor</button>
                                </div>
                            </div>
                        </li>
                    ))}
                </ul>
                )}
            </div>
            {showPlaySetupModal && <PlaySetupModal onPlay={() => onNavigate("play")} isPending={newSession.isPending} world={worldMetadata} onClose={() => setShowPlaySetupModal(false)}/>}
        </div>
        
    )
}

export default Landing