import { useEffect , useRef, useState } from "react"
import "./PlaySetupModal.css"
import StorylinesSetup from "./StorylinesSetup"
import CharacterSetup from "./CharacterSetup"

function PlaySetupModal({ 
    worldTitle,
    initialWorldDescription,
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

    useEffect(() => {
        dialogRef.current.showModal()
    }, [])

    function getSetupDescriptions() {
        return {
            world_description: worldDescRef.current.value,
            character_description: characterRef.current.value,
            story_focus_description: storyFocusRef.current.value,
        }
    }


    function handleOnSubmit() {
        const worldDescription = worldDescRef.current.value
        const characterDescription = characterRef.current.value
        const storyFocusDescription = storyFocusRef.current.value

        onSubmit(worldDescription, characterDescription, storyFocusDescription, storylines)
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
                <p className="modal-caption">World name</p>
                <h1 className="modal-title">{worldTitle}</h1>
            </div>
            <div className="modal-content">
                <div className="modal-container">
                    <div className="modal-container">
                        <div className="modal-component">
                            <p className="modal-caption">World description</p>
                            <textarea 
                                ref={worldDescRef}
                                className="modal-text"
                                defaultValue={initialWorldDescription}
                            ></textarea>
                        </div>
                        <div className="modal-component">
                            <p className="modal-caption">Story focus</p>
                            <textarea 
                                ref={storyFocusRef}
                                className="modal-text"
                                defaultValue={initialStoryFocus}
                            ></textarea>
                        </div>
                    </div>
                    <CharacterSetup/>
                </div>
                <div className="modal-container-2">
                    <StorylinesSetup
                        storylines={storylines}
                        setStorylines={setStorylines}
                        getSetupDescriptions={getSetupDescriptions}
                        regionLookup={regionLookup}
                        componentLookup={componentLookup}
                    />
                    <div>
                        <button onClick={handleGenerateHiddenContext}>Generate hidden context</button>
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