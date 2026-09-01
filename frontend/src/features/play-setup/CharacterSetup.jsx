import EditableList from "../../components/EditableList"
import { useState } from 'react'

function CharacterSetup() {
    const [inventory, setInventory] = useState([{name: "Sword"}])
    return (
        <div>
            <h2 className="modal-caption">Character Setup</h2>
            <div className="character-container">
                <div>
                    <p className="modal-caption">Character description</p>
                    <textarea className="modal-text"/>
                    <button>Generate Details</button>
                </div>
                <div className="character-content">
                    <div>
                        <p className="modal-caption">Notebook</p>
                        <textarea className="modal-text"/>
                        <p className="modal-caption">Inventory</p>
                        <EditableList
                            items={inventory}
                            onItemsChange={setInventory}
                            createItem={() => ({ id: crypto.randomUUID(), name: "" })}
                            renderItem={(invItem, onChange) => (
                                <input value={invItem.name} onChange={(e) => onChange({...invItem, name: e.target.value})} />
                            )}
                        />
                    </div>
                    <div>
                        <p className="modal-caption">Stats</p>
                        <p>Strength: 5/10</p>
                        <p>Stamina: 5/10</p>
                        <p>Perception: 5/10</p>
                        <p>Charisma: 5/10</p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default CharacterSetup