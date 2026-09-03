import './StorylinesSetup.css'
    
import { useState } from "react"
import { streamRequest } from "../../utils/streaming"

function StorylinesSetup({
    storylines,
    setStorylines,
    getSetupDescriptions,
    regionLookup,
    componentLookup,
    handleGenerateHiddenContext,
}) {
    const [reasoning, setReasoning] = useState('')
    const [isStreaming, setIsStreaming] = useState(false)

    const [toggleTextbox, setToggleTextbox] = useState('storylines') //'storylines' or 'reasoning'

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
            <div>
                <button onClick={() => setToggleTextbox('storylines')} className="modal-caption">Storylines</button>
                <span className="modal-caption"> / </span>
                <button onClick={() => setToggleTextbox('reasoning')} className="modal-caption">Reasoning</button>
            </div>
            <textarea
                value={toggleTextbox === 'storylines' ? storylines : reasoning}
                disabled={isStreaming}
                onChange={(e) => toggleTextbox === 'storylines' ? setStorylines(e.target.value) : setReasoning(e.target.value)}
                className="modal-text variable-height"
            />
            <div>
                <button onClick={generateStorylines}>Generate Storylines</button>
                <button onClick={handleGenerateHiddenContext}>Generate hidden context</button>
            </div>
        </div>
    )
}

export default StorylinesSetup