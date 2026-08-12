import { useEffect , useRef } from "react"
import { useWorldsQuery } from '../queries/queries'

function PlaySetupModal({ onPlay , isPending , world , onClose}) {
    const dialogRef = useRef(null)

    useEffect(() => {
        dialogRef.current.showModal()
    }, [])

    return (
        <dialog ref={dialogRef} className="modal play-setup-modal" onClose={onClose}>
            <p className="modal-title-caption">World name</p>
            <h1 className="modal-title">{world.name}</h1>
            <p className="modal-title-caption">Description</p>
            <p className="modal-text">{world.story_setup.world_description}</p>
            <p className="modal-title-caption">Character</p>
            <p className="modal-text">{world.story_setup.character_description}</p>
            <p className="modal-title-caption">Story focus</p>
            <p className="modal-text">{world.story_setup.story_focus_description}</p>
            <button onClick={onPlay} disabled={isPending}>
                {isPending ? "Loading world…" : "Play"}
            </button>
        </dialog>
    )
}

export default PlaySetupModal