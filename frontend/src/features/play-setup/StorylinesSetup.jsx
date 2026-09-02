import './StorylinesSetup.css'
    
import { useState } from "react"
import { streamRequest } from "../../utils/streaming"

function StorylinesSetup({
    storylines,
    setStorylines,
    getSetupDescriptions,
    regionLookup,
    componentLookup,
}) {
    const [reasoning, setReasoning] = useState('')
    const [isStreaming, setIsStreaming] = useState(false)

    async function generateStorylines() {
        const payload = {
            ...getSetupDescriptions(),
            region_lookup: regionLookup,
            component_lookup: componentLookup,
        }
        setStorylines('')
        setReasoning('')
        setIsStreaming(true)
        await streamRequest('/api/setup/generate-storylines', payload, {
            token: (token) => setStorylines(prev => prev + token),
            reasoning: (token) => setReasoning(prev => prev + token),
            done: (payload) => {
                setStorylines(payload)
                setIsStreaming(false)
            },
            error: (payload) => console.log(JSON.parse(payload)),
        })
    }

    return (
        <div className="modal-component">
            <p className="modal-caption">Storylines</p>
            <textarea
                value={storylines}
                disabled={isStreaming}
                onChange={(e) => setStorylines(e.target.value)}
                className="modal-text variable-height"
            />
            <textarea
                value={reasoning}
                disabled={true}
                className="modal-text variable-height"
            />
            <div>
                <button onClick={generateStorylines}>Generate Storylines</button>
            </div>
        </div>
    )
}

export default StorylinesSetup