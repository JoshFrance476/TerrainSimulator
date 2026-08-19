import { useEffect , useRef } from "react"
import { useWorldsQuery } from '../queries/queries'

function PlaySetupModal({ onPlay , isPending , world , onClose}) {
    const dialogRef = useRef(null)

    const worldDescRef = useRef(null)
    const characterRef = useRef(null)
    const storyFocusRef = useRef(null)

    useEffect(() => {
        dialogRef.current.showModal()
    }, [])

    return (
        <dialog ref={dialogRef} className="modal play-setup-modal" onClose={onClose} spellCheck={false}>
            <div className="modal-header">
                <p className="modal-title-caption">World name</p>
                <h1 className="modal-title">{world.name}</h1>
            </div>
            <div className="modal-content">
                <div className="modal-component">
                    <p className="modal-title-caption">World description</p>
                    <textarea 
                        ref={worldDescRef}
                        className="modal-text"
                        defaultValue={world.story_setup.world_description}
                    ></textarea>
                </div>
                <div className="modal-component">
                    <p className="modal-title-caption">Character description</p>
                    <textarea 
                        ref={characterRef}
                        className="modal-text"
                        defaultValue={world.story_setup.character_description}
                    ></textarea>
                </div>
                <div className="modal-component">
                    <p className="modal-title-caption">Story focus</p>
                    <textarea 
                        ref={storyFocusRef}
                        className="modal-text"
                        defaultValue={world.story_setup.story_focus_description}
                    ></textarea>
                </div>
            </div>
            <div className="modal-actions">
                <button className="modal-close-button" onClick={onClose}>Close</button>
                <button onClick={() => onPlay(worldDescRef.current.value, characterRef.current.value, storyFocusRef.current.value)} disabled={isPending}>
                    {isPending ? "Loading world…" : "Play"}
                </button>
            </div>
        </dialog>
    )
}

export default PlaySetupModal