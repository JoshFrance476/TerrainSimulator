import { useState } from 'react'
import LocationTab from './info-tabs/LocationTab'
import QuestTab from './info-tabs/QuestTab'
import CharacterTab from './info-tabs/CharacterTab'
function InfoWindow({ selectedCell, player }) {
    const [activeTab, setActiveTab] = useState('location') // 'location', 'character','npcs','quests', "story"
    return (
        <div className="info-window">
            <div className="tab-bar">
                <button 
                    className={activeTab === 'location' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('location')}
                >
                    Location
                </button>
                <button
                    className={activeTab === 'character' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('character')}
                >
                    Character
                </button>
                <button
                    className={activeTab === 'npcs' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('npcs')}
                >
                    NPCs
                </button>
                <button
                    className={activeTab === 'quests' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('quests')}
                >
                    Quests
                </button>
            </div>
            {activeTab === 'location' && <LocationTab selectedCell={selectedCell} />}
            {activeTab === 'character' && <CharacterTab player={player} />}
            {activeTab === 'npcs' && (<div>
                <p>NPC information will go here.</p>
            </div>
            )}
            {activeTab === 'quests' && <QuestTab />}
        </div>
    )
}

export default InfoWindow