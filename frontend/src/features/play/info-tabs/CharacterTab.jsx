
import { useStory } from '../../../hooks/useStory'

function CharacterTab() {
    const { characterHistory: fetchedCharacterHistory } = useStory()
    return (
        <div>
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