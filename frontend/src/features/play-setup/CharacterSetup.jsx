import { useState } from 'react'

function CharacterSetup( {getSetupDescriptions} ) {
    const [inventory, setInventory] = useState([]) // id, name
    const [stats, setStats] = useState([]) // id, name, value
    const [notebook, setNotebook] = useState("")

    const updateItem = (id, name) =>
        setInventory((prev) => prev.map((item) => (item.id === id ? { ...item, name } : item)))

    const removeItem = (id) =>
        setInventory((prev) => prev.filter((item) => item.id !== id))

    const addItem = (name = "") =>
        setInventory((prev) => [...prev, { id: crypto.randomUUID(), name }]) 


    const updateStat = (id, changes) =>
        setStats((prev) => prev.map((stat) => (stat.id === id ? { ...stat, ...changes } : stat)))

    const addStat = (name = "", value = 0) =>
        setStats((prev) => [...prev, { id: crypto.randomUUID(), name, value }])

    const removeStat = (id) =>
        setStats((prev) => prev.filter((stat) => stat.id !== id))

    async function generateCharacterSetup() {
        const worldSetup = getSetupDescriptions()
        const payload = {
            character_description: worldSetup.character_description,
            world_description: worldSetup.world_description,
            focus_description: worldSetup.story_focus_description
        }

        const response = await fetch('/api/setup/generate-character-setup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const content = await response.json();

        
        setInventory(content.inventory.map((item) => ({
            id: crypto.randomUUID(),
            name: item,
        })))

        setStats(content.stats.map((stat) => ({
            id: crypto.randomUUID(),
            name: stat.stat_name,
            value: stat.value,
        })))

        setNotebook(content.notebook)
    }

    return (
        <div>
            <h2 className="modal-caption">Character Setup</h2>
            <div className="character-container">
                <div>
                    <button onClick={() => generateCharacterSetup()}>Generate Details</button>
                </div>
                <div className="character-content">
                    <div className='modal-container-even'>
                        <div className='flex-column'>
                            <p className="modal-caption">Notebook</p>
                            <textarea 
                                className="modal-text fill"
                                value={notebook}
                                onChange={(e) => setNotebook(e.target.value)}
                            />
                        </div>
                        <div>
                            <p className="modal-caption">Stats</p>
                            <ul className='stat-list'>
                            {stats.map((stat) => (
                                <li className='stat-list-item' key={stat.id}>
                                    <input className='stat-list-name' value={stat.name} onChange={(e) => updateStat(stat.id, {name: e.target.value})}/>
                                    <input className="stat-list-value" type='number' value={stat.value} onChange={(e) => updateStat(stat.id, {value: e.target.valueAsNumber})}/>
                                    <button className='stat-list-remove' onClick={() => removeStat(stat.id)}>-</button>
                                </li>
                            ))}
                            </ul>
                            <button onClick={() => addStat()}>Add</button>
                        </div>
                    </div>
                    <div>
                        <h2 className='modal-caption'>Inventory</h2>
                        <ul className='inventory-list'>
                        {inventory.map((item) => (
                            <li className='inventory-list-item' key={item.id}>
                                <input className = 'inventory-list-name' value={item.name} onChange={(e) => updateItem(item.id, e.target.value)} />
                                <button className='inventory-list-remove' onClick={() => removeItem(item.id)}>-</button>
                            </li>
                        ))}
                        </ul>
                        <button onClick={() => addItem()}>Add</button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default CharacterSetup