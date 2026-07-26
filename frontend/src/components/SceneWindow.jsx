import { useEffect, useState } from 'react'

function SceneWindow( { selectedCell } ) {
    const [scene, setScene] = useState(null)
    const [streamedOutput, setStreamedOutput] = useState('')

    async function updateScene() {
        const res = await fetch('/api/scene')

        const { scene } = await res.json()

        setScene(scene)

        return scene
    }

    async function callPrompt() {
        setStreamedOutput('')
        const res = await fetch('/api/scene/prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ x: selectedCell ? selectedCell.x : null, y: selectedCell ? selectedCell.y : null })
        })

        if (!res.ok) {
            console.error('Prompt call failed:', await res.text())
            return
        }

        const { stream_id } = await res.json()

        const source = new EventSource(`/api/stream?id=${stream_id}`)
        
        source.addEventListener('data', (e) => {
            setStreamedOutput((prev) => prev + e.data)
        })
        source.addEventListener('done', () => {
            source.close()
            updateScene()
            setStreamedOutput('')
        })
        source.onerror = () => source.close()
    }

    async function submitAction({ action }) {
        const res = await fetch('/api/scene/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        })

        if (!res.ok) {
            console.error('Action submission failed:', await res.text())
            return
        }
        
        const updatedScene = await updateScene()

        console.log(updatedScene)

        if (!updatedScene.ended) {
            await callPrompt()
        }
        
    }

    function startNewScene() {
        setScene(null)
        callPrompt()
    }

    useEffect(() => {console.log(scene)}, [scene])

    useEffect(() => {updateScene()}, [])


    return (
        <div className="scene-window">
            <div>
                <button onClick={startNewScene}>Send</button>
            </div>

            {!scene && <p>No active scene.</p>}

            {scene && (
                <>
                    {scene.history.map((interaction, index) => (
                        <div key={index}>
                            <p>{interaction.situation}</p>
                            <p className="action">{interaction.action}</p>
                        </div>
                    ))}

                    {scene.pending && (
                        <div>
                            <p>{scene.pending.description}</p>
                            {scene.pending.actions.map((a, index) => (
                                <button key={index} onClick={() => submitAction({ action: a.action })}>
                                    {a.action} - {a.exit_flag ? 'Exit' : 'Continue'}
                                </button>
                            ))}
                        </div>
                    )}
                </>
            )}
            <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', width: '100%', boxSizing: 'border-box' }}>
                {streamedOutput}
            </pre>
        </div>
    )
}

export default SceneWindow