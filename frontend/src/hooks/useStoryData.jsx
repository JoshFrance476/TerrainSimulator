import { useEffect, useState } from 'react'

export function useStoryData() {
    const [storyVersion, setStoryVersion] = useState(0)
    const [characterHistory, setCharacterHistory] = useState(null)
    const [questsList, setQuestsList] = useState(null) 

    useEffect(() => {
        async function fetchStoryData() {
            const res = await fetch('/api/story')
            const data = await res.json()
            setCharacterHistory(data.character_history)
            setQuestsList(data.quests_list)
            setStoryVersion(data.version)
        }
        fetchStoryData()
    }, [storyVersion])

    return {
        characterHistory,
        questsList,
        storyVersion,
        setStoryVersion
    }
}
