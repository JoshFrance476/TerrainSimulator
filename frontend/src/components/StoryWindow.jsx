import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { usePlayer } from '../hooks/usePlayer'
import { useSubmitActionMutation, promptScene, sceneKey, storyKey, tokenUsageKey, useSceneQuery } from '../queries/queries'
import EngineTab from './scene-tabs/EngineTab'
import SceneTab from './scene-tabs/SceneTab'

function StoryWindow() {
    const [activeTab, setActiveTab] = useState('scene') // 'scene', 'engine'
    const [streamedOutput, setStreamedOutput] = useState('')

    const { data: scene, isLoading: sceneLoading } = useSceneQuery()
    const { playerLocation } = usePlayer()
    const queryClient = useQueryClient()
    const submitAction = useSubmitActionMutation()

    async function callPrompt() {
        if (!playerLocation) {
            console.error('Player location is not available.')
            return
        }
        setStreamedOutput('')
        const { stream_id } = await promptScene({ x: playerLocation.x, y: playerLocation.y })

        const source = new EventSource(`/api/stream?id=${stream_id}`)
        
        source.addEventListener('data', (e) => {
            setStreamedOutput((prev) => prev + e.data)
        })
        source.addEventListener('done', () => {
            source.close()
            setStreamedOutput('')
            queryClient.invalidateQueries({ queryKey: sceneKey })
            queryClient.invalidateQueries({ queryKey: storyKey })
            queryClient.invalidateQueries({ queryKey: tokenUsageKey })
        })
        source.onerror = () => source.close()
    }

    async function handleSubmitAction({ action }) {
        const { ended } = await submitAction.mutateAsync(action)
        if (!ended) {
            callPrompt()
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
                onStartNewScene={() => { callPrompt() }}
                onRetryPrompt={callPrompt}
                onSubmitAction={handleSubmitAction}
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