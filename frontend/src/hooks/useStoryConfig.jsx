import { useState, useEffect } from 'react'

export function useStoryConfig() {
    const [interactionPrompt, setInteractionPrompt] = useState('')
    const [sceneGuidePrompt, setSceneGuidePrompt] = useState('')

    const [model, setModel] = useState('')

    useEffect(() => {
        async function fetchSceneGuidePrompt() {
            const res = await fetch('/api/scene/templates/scene-guide')
            const data = await res.json()
            setSceneGuidePrompt(data.text)
        }
        fetchSceneGuidePrompt()
    }, 
    [])
    
    useEffect(() => {
        async function fetchInteractionPrompt() {
            const res = await fetch('/api/scene/templates/interaction')
            const data = await res.json()
            setInteractionPrompt(data.text)
        }
        fetchInteractionPrompt()
    }, [])
    
    async function saveInteractionPrompt() {
        const res = await fetch('/api/scene/templates/interaction', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: interactionPrompt })
        })

        if (!res.ok) {
            console.error('Failed to save interaction prompt:', await res.text())
        }
    }

    async function saveSceneGuidePrompt() {
        const res = await fetch('/api/scene/templates/scene-guide', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: sceneGuidePrompt })
        })
        if (!res.ok) {
            console.error('Failed to save scene guide prompt:', await res.text())
        }
    }

    return {
        interactionPrompt,
        setInteractionPrompt,
        sceneGuidePrompt,
        setSceneGuidePrompt,
        model,
        setModel,
        saveInteractionPrompt,
        saveSceneGuidePrompt
    }
}