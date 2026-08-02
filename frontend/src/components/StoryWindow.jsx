import { useState, useRef, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { usePlayer } from '../hooks/usePlayer'
import { useSubmitActionMutation, promptScene, sceneKey, storyKey, tokenUsageKey, useSceneQuery } from '../queries/queries'
import EngineTab from './scene-tabs/EngineTab'
import SceneTab from './scene-tabs/SceneTab'

function StoryWindow() {
    const [activeTab, setActiveTab] = useState('scene') // 'scene', 'engine'
    const [streamedOutput, setStreamedOutput] = useState('')

    const { data: scene } = useSceneQuery()
    const { playerLocation } = usePlayer()
    const queryClient = useQueryClient()
    const submitAction = useSubmitActionMutation()

    const sourceRef = useRef(null)

    // close any open stream when the component unmounts
    useEffect(() => () => sourceRef.current?.close(), [])

    function closeStream() {
        sourceRef.current?.close()
        sourceRef.current = null
    }

    async function callPrompt() {
        if (!playerLocation) {
            console.error('Player location is not available.')
            return
        }

        closeStream()
        setStreamedOutput('')

        let stream_id
        try {
            ({ stream_id } = await promptScene({ x: playerLocation.x, y: playerLocation.y }))
        } catch (err) {
            console.error('Failed to start scene:', err)
            return
        }

        const source = new EventSource(`/api/stream?id=${stream_id}`)
        sourceRef.current = source
        
        source.addEventListener('data', (e) => {
            setStreamedOutput((prev) => prev + e.data)
        })
        source.addEventListener('done', () => {
            closeStream()
            setStreamedOutput('')
            queryClient.invalidateQueries({ queryKey: sceneKey })
            queryClient.invalidateQueries({ queryKey: storyKey })
            queryClient.invalidateQueries({ queryKey: tokenUsageKey })
        })
        source.addEventListener('stream_error', (e) => {
            const { error, detail } = JSON.parse(e.data)
            console.error(`${error}: ${detail}`)
            closeStream()
        })
        source.onerror = () => closeStream()
    }

    async function handleSubmitAction({ action }) {
        try {
            const { ended } = await submitAction.mutateAsync(action)
            if (!ended) await callPrompt()
        } catch (err) {
            console.error('Action failed:', err)
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
                onStartNewScene={callPrompt}
                onRetryPrompt={callPrompt}
                onSubmitAction={handleSubmitAction}
            />}
            {activeTab === 'engine' && <EngineTab/>}
        </div>
    )
}

export default StoryWindow