import { useState, useEffect } from 'react'
import { useStoryConfig } from '../hooks/useStoryConfig'
import EngineTab from './scene-tabs/EngineTab'
import SceneTab from './scene-tabs/SceneTab'

function StoryWindow({ playerLocation }) {
    const [activeTab, setActiveTab] = useState('scene') // 'scene', 'engine'
    const [scene, setScene] = useState(null)
    const [streamedOutput, setStreamedOutput] = useState('')

    const { interactionPrompt, setInteractionPrompt, sceneGuidePrompt, setSceneGuidePrompt, 
        saveInteractionPrompt, saveSceneGuidePrompt } = useStoryConfig()


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
            body: JSON.stringify({ x: playerLocation ? playerLocation.x : null, y: playerLocation ? playerLocation.y : null })
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

    return (
        <div className="story-window">
            <div className="tab-bar">
                <button
                    className={activeTab === 'scene' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('scene')}
                >
                    Scene
                </button>
                <button
                    className={activeTab === 'engine' ? 'tab active' : 'tab'}
                    onClick={() => setActiveTab('engine')}
                >
                    Engine
                </button>
            </div>
            {activeTab === 'scene' && <SceneTab 
                playerLocation={playerLocation}
                scene={scene}
                streamedOutput={streamedOutput}
                onStartNewScene={() => { setScene(null); callPrompt(); }}
                onSubmitAction={submitAction}
            />}
            {activeTab === 'engine' && <EngineTab 
                interactionPrompt={interactionPrompt}
                setInteractionPrompt={setInteractionPrompt}
                onInteractionSave={saveInteractionPrompt}
                sceneGuidePrompt={sceneGuidePrompt}
                setSceneGuidePrompt={setSceneGuidePrompt}
                onSceneGuideSave={saveSceneGuidePrompt}
            />}
        </div>
    )
}

export default StoryWindow