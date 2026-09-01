import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { usePlayer } from '../../hooks/usePlayer'
import { useSubmitActionMutation, useGenerateSceneSummaryMutation, sceneKey, storyKey, tokenUsageKey, useSceneQuery } from '../../queries/queries'
import EngineTab from './scene-tabs/EngineTab'
import SceneTab from './scene-tabs/SceneTab'
import {streamRequest} from "../../utils/streaming"

function StoryWindow({ user }) {
    const [activeTab, setActiveTab] = useState('scene') // 'scene', 'engine'
    const [streamedOutput, setStreamedOutput] = useState('')

    const { data: scene } = useSceneQuery()
    const { playerLocation } = usePlayer()
    const queryClient = useQueryClient()
    const submitAction = useSubmitActionMutation()
    const generateSummary = useGenerateSceneSummaryMutation()

    const [sceneGuideIsStreaming, setSceneGuideIsStreaming] = useState(false)
    const [interactionIsStreaming, setInteractionIsStreaming] = useState(false)

    async function generateSceneGuide() {
        setSceneGuideIsStreaming(true)
        await streamRequest('/api/scene/generate-guide', { x: playerLocation.x, y: playerLocation.y }, {
            token: (token) => {
                setStreamedOutput((prev) => prev + token)
                console.log(token)
            },
            done: () => {
                setStreamedOutput('')
                setSceneGuideIsStreaming(false)
                queryClient.invalidateQueries({ queryKey: sceneKey })
                queryClient.invalidateQueries({ queryKey: storyKey })
                queryClient.invalidateQueries({ queryKey: tokenUsageKey })
            },
            error: (payload) => console.log(JSON.parse(payload))
        })
    }

    async function generateInteraction() {
        setInteractionIsStreaming(true)
        await streamRequest('/api/scene/generate-interaction', {}, {
            token: (token) => {
                setStreamedOutput((prev) => prev + token)
                console.log(token)
            },
            done: () => {
                setStreamedOutput('')
                setInteractionIsStreaming(false)
                queryClient.invalidateQueries({ queryKey: sceneKey })
                queryClient.invalidateQueries({ queryKey: storyKey })
                queryClient.invalidateQueries({ queryKey: tokenUsageKey })
            },
            error: (payload) => console.log(JSON.parse(payload))
        })
    }

    async function handleSubmitAction({ action }) {
        try {
            const { ended } = await submitAction.mutateAsync(action)
            if (!ended) await generateInteraction()
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
                onStartNewScene={generateSceneGuide}
                onRetryPrompt={generateSceneGuide}
                onSubmitAction={handleSubmitAction}
                user={user}
                sceneGuideIsStreaming={sceneGuideIsStreaming}
                interactionIsStreaming={interactionIsStreaming}
                onPromptInteraction={generateInteraction}
                onSummariseScene={() => generateSummary.mutate()}
            />}
            {activeTab === 'engine' && <EngineTab/>}
        </div>
    )
}

export default StoryWindow