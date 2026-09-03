import { useEffect , useRef, useState } from "react"
import "./PlaySetupModal.css"
import StorylinesSetup from "./StorylinesSetup"
import CharacterSetup from "./CharacterSetup"
import WorldSetup from "./WorldSetup"


function PlaySetupModal({ 
    worldTitle,
    initialWorldDescription,
    initialStoryFocus,
    initialStorylines,
    initialCharacterSetup,
    initialRegionLookup,
    initialComponentLookup,
    submitLabel,
    onSubmit , 
    isPending , 
    onClose 
}) {
    const dialogRef = useRef(null)

    const worldDescRef = useRef(null)
    const storyFocusRef = useRef(null)
    const characterDescriptionRef = useRef(null)

    const [storylines, setStorylines] = useState(initialStorylines)

    const [regionLookup, setRegionLookup] = useState(initialRegionLookup)
    const [componentLookup, setComponentLookup] = useState(initialComponentLookup)


    useEffect(() => {
        dialogRef.current.showModal()
    }, [])

    function getSetupDescriptions() {
        return {
            world_description: worldDescRef.current.value,
            story_description: storyFocusRef.current.value,
            character_description: characterDescriptionRef.current.value
        }
    }


    function handleOnSubmit() {
        const worldDescription = worldDescRef.current.value
        const storyDescription = storyFocusRef.current.value
        const characterDescription = characterDescriptionRef.current.value

        onSubmit(worldDescription, characterDescription, storyDescription, regionLookup, componentLookup)
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
        setRegionLookup(hiddenContext.regions)
        setComponentLookup(hiddenContext.components)
        console.log(hiddenContext)
    }



    return (
        <dialog ref={dialogRef} className="modal play-setup-modal" onClose={onClose} spellCheck={false}>
            <div className="modal-header">
                <p className="modal-caption">World name</p>
                <h1 className="modal-title">{worldTitle}</h1>
            </div>
            <div className="modal-content">
                <div className="modal-container-left">
                    <div className="modal-container-three">
                        <div className="modal-component">
                            <p className="modal-caption">World description</p>
                            <textarea 
                                ref={worldDescRef}
                                className="modal-text"
                                defaultValue={initialWorldDescription}
                            ></textarea>
                        </div>
                        <div className="modal-component">
                            <p className="modal-caption">Playthrough style and tone</p>
                            <textarea 
                                ref={storyFocusRef}
                                className="modal-text"
                                defaultValue={initialStoryFocus}
                            ></textarea>
                        </div>
                        <div className="modal-component">
                            <p className="modal-caption">Character Description</p>
                            <textarea 
                                ref={characterDescriptionRef}
                                className="modal-text"
                                defaultValue={initialCharacterSetup}
                            ></textarea>
                        </div>
                    </div>
                    <CharacterSetup
                        getSetupDescriptions={getSetupDescriptions}
                    />
                </div>
                <div className="modal-container-right">
                    <StorylinesSetup
                        storylines={storylines}
                        setStorylines={setStorylines}
                        getSetupDescriptions={getSetupDescriptions}
                        regionLookup={regionLookup}
                        componentLookup={componentLookup}
                        handleGenerateHiddenContext={handleGenerateHiddenContext}
                    />
                    <WorldSetup 
                        componentLookup={componentLookup}
                        regionLookup={regionLookup}
                    />
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