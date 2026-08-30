import { useEffect , useRef, useState } from "react"
import "./PlaySetupModal.css"
import {streamRequest} from "../utils/streaming"

function PlaySetupModal({ 
    worldTitle,
    initialWorldDescription,
    initialCharacterDescription,
    initialStoryFocus,
    initialStorylines,
    regionLookup,
    componentLookup,
    submitLabel,
    onSubmit , 
    isPending , 
    onClose 
}) {
    const dialogRef = useRef(null)

    const worldDescRef = useRef(null)
    const characterRef = useRef(null)
    const storyFocusRef = useRef(null)

    const [storylines, setStorylines] = useState(initialStorylines)
    const [storylinesIsStreaming, setStorylinesIsStreaming] = useState(false)

    useEffect(() => {
        dialogRef.current.showModal()
    }, [])

    async function handleGenerateStorylines() {
        await generateStorylines()
    }

    function handleOnSubmit() {
        const worldDescription = worldDescRef.current.value
        const characterDescription = characterRef.current.value
        const storyFocusDescription = storyFocusRef.current.value

        onSubmit(worldDescription, characterDescription, storyFocusDescription, storylines)
    }

    async function generateStorylines() {
        const payload = {
            world_description: worldDescRef.current.value,
            character_description: characterRef.current.value,
            story_focus_description: storyFocusRef.current.value,
            region_lookup: regionLookup,
            component_lookup: componentLookup
        }
        setStorylines('')
        setStorylinesIsStreaming(true)
        await streamRequest('/api/setup/generate-storylines', payload, {
            token: (token) => {
                setStorylines(prev => prev + token)
                console.log(token)
            },
            done: (payload) => {
                setStorylines(payload)
                setStorylinesIsStreaming(false)
            },
            error: (payload) => console.log(JSON.parse(payload))
        })
    }
    
    async function generateHiddenContext(storylines) {
        const payload = { storylines }
        console.log("Generating hidden context with payload:", payload)
        const response = await fetch('/api/setup/generate-hidden-context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return response.json();
    }

    async function handleGenerateHiddenContext() {
        const hiddenContext = await generateHiddenContext(storylines)
        console.log("Hidden context:", hiddenContext)
    }

    return (
        <dialog ref={dialogRef} className="modal play-setup-modal" onClose={onClose} spellCheck={false}>
            <div className="modal-header">
                <p className="modal-title-caption">World name</p>
                <h1 className="modal-title">{worldTitle}</h1>
            </div>
            <div className="modal-content">
                <div className="modal-container">
                    <div className="modal-component">
                        <p className="modal-title-caption">World description</p>
                        <textarea 
                            ref={worldDescRef}
                            className="modal-text"
                            defaultValue={initialWorldDescription}
                        ></textarea>
                    </div>
                    <div className="modal-component">
                        <p className="modal-title-caption">Character description</p>
                        <textarea 
                            ref={characterRef}
                            className="modal-text"
                            defaultValue={initialCharacterDescription}
                        ></textarea>
                    </div>
                    <div className="modal-component">
                        <p className="modal-title-caption">Story focus</p>
                        <textarea 
                            ref={storyFocusRef}
                            className="modal-text"
                            defaultValue={initialStoryFocus}
                        ></textarea>
                    </div>
                </div>
                <div className="modal-container-2">
                    <div className="modal-component">
                        <p className="modal-title-caption">Storylines</p>
                        <textarea 
                            value={storylines}
                            disabled={storylinesIsStreaming}
                            onChange={(e) => setStorylines(e.target.value)}
                            className="modal-text variable-height"
                        />
                        <div>
                            <button onClick={handleGenerateStorylines}>Generate Storylines</button>
                            <button onClick={handleGenerateHiddenContext}>Generate hidden context</button>
                        </div>
                    </div>
                    <div className="modal-container-vertical">
                        <div>
                            <h3>Regions</h3>
                            <div className="modal-list">
                                {Object.entries(regionLookup).map(([key, region]) => (
                                    <div key={key}>{region.title} - {region.visible_description}</div>
                                ))}
                            </div>
                        </div>
                        <div>
                            <h3>Components</h3>
                            <div className="modal-list">
                                {Object.entries(componentLookup).map(([key, component]) => (
                                    <div key={key}>{component.name} - {component.description}</div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div className="modal-actions">
                <button className="modal-close-button" onClick={onClose}>Close</button>
                <button onClick={handleOnSubmit} disabled={isPending}>
                    {isPending ? "Loading world…" : submitLabel}
                </button>
            </div>
        </dialog>
    )
}

export default PlaySetupModal