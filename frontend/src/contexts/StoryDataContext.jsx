
import { createContext, useContext } from 'react'
import { useStoryData } from '../hooks/useStoryData'

const StoryDataContext = createContext(null)

export function StoryDataProvider({ children }) {
    const storyData = useStoryData()
    return (
        <StoryDataContext.Provider value={storyData}>
            {children}
        </StoryDataContext.Provider>
    )
}

export function useStoryDataContext() {
    const context = useContext(StoryDataContext)
    if (context === null) {
        throw new Error('useStoryDataContext must be used inside a StoryDataProvider')
    }
    return context
}