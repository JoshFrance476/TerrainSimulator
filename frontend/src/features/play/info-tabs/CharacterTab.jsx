
import { useStory } from '../../../hooks/useStory'

function CharacterTab({ player }) {
    const { characterHistory: fetchedCharacterHistory } = useStory()
    return (    
        <div>
            <p>Stats:</p>
            {player.stats.map((entry, index) => (
                <p key={index}>{entry.name}: {entry.value}</p>
            ))}
            <p>Inventory:</p>
            {player.inventory.map((entry, index) => (
                <p key={index}>{entry.name}</p>
            ))}
            <p>Notebook:</p>
            {player.notebook.map((entry, index) => (
                <p key={index}>{entry}</p>
            ))}
            {fetchedCharacterHistory && fetchedCharacterHistory.length > 0 ? (
                <ul>
                    {fetchedCharacterHistory.map((entry, index) => (
                        <li key={index}>{entry}</li>
                    ))}
                </ul>
            ) : (
                <p>No character history available.</p>
            )}
        </div>
    )
}

export default CharacterTab